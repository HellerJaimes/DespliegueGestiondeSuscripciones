from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
from main.forms import CustomUserCreationForm
from firebase_config import db, auth, registrar_usuario
from main.models import UsuarioLocal
import requests
import json
from suscripciones.models import Suscripcion
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache   
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


def home(request):
    return render(request, 'home.html')

def quienessomos(request):
    return render(request, 'quienessomos.html')

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            username = form.cleaned_data.get("username")

            resultado = registrar_usuario(email=email, password=password, nombre=username)

            if isinstance(resultado, str) and resultado.startswith("Error"):
                messages.error(request, resultado)
            else:
                # 🔥 Crear el usuario también en la base de datos local
                uid = resultado  # Asumiendo que registrar_usuario te devuelve el UID

                UsuarioLocal.objects.create(
                    uid=uid,
                    email=email,
                    nombre=username
                )

                messages.success(request, "Usuario creado exitosamente")
                return redirect("login")  # O donde quieras
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)  # 👈 Agregado aquí
    else:
        form = CustomUserCreationForm()
    
    return render(request, "signup.html", {"form": form})

def login_view(request):
    if request.session.get("user"):
        return redirect("menu")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Debes ingresar un correo y una contraseña.")
            return render(request, "login.html")

        try:
            api_key = settings.FIREBASE_API_KEY
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            payload = {"email": email, "password": password, "returnSecureToken": True}
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, data=json.dumps(payload), headers=headers)
            result = response.json()

            if "idToken" in result:  # Si Firebase autentica correctamente al usuario
                uid = result["localId"]

                # Consultar Firestore para obtener el nombre del usuario
                user_doc = db.collection("usuarios").document(uid).get()
                if user_doc.exists:
                    nombre_usuario = user_doc.to_dict().get("nombre", "Usuario")
                else:
                    nombre_usuario = "Usuario"

                # Verificar si el usuario ya existe en la base de datos SQLite
                usuario_local, created = UsuarioLocal.objects.get_or_create(
                    uid=uid,
                    email=email,
                    defaults={"nombre": nombre_usuario}
                )

                # Si el usuario es nuevo, guardamos su nombre desde Firestore en la base de datos SQLite
                if created:
                    usuario_local.nombre = nombre_usuario
                    usuario_local.save()

                # Guardamos los datos del usuario en la sesión
                request.session["user"] = {
                    "email": email,
                    "uid": uid,
                    "nombre": nombre_usuario,
                    "origen": "firebase"  # Indicamos que el usuario viene de Firebase
                }

                messages.success(request, "¡Se ha iniciado sesión correctamente!")
                return redirect("suscripciones_dashboard")  # Verifica que esta URL esté definida correctamente

            else:
                messages.error(request, "Error de autenticación con Firebase. Verifica tus credenciales.")

        except requests.exceptions.RequestException as e:
            messages.error(request, "Error de conexión. Por favor, intenta más tarde.")

    return render(request, "login.html")

def logout_view(request):
    request.session.flush()  # Limpia la sesión
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('home')

@never_cache
def menu(request):
    user_session = request.session.get("user")
    if not user_session:
        return redirect("login")

    try:
        usuario_local = UsuarioLocal.objects.get(uid=user_session.get("uid"))
    except UsuarioLocal.DoesNotExist:
        return redirect("login")

    suscripciones = Suscripcion.objects.filter(usuario_local=usuario_local)

    categorias = {}
    for s in suscripciones:
        categorias[s.categoria] = categorias.get(s.categoria, 0) + 1

    activas = suscripciones.filter(activo=True).count()
    inactivas = suscripciones.filter(activo=False).count()

    gasto_mensual = {}
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    for mes in meses:
        gasto_mensual[mes] = 0

    for suscripcion in suscripciones.filter(activo=True):
        gasto_mensual[meses[suscripcion.fecha_pago.month - 1]] += float(suscripcion.costo)

    context = {
        "nombre": user_session.get("nombre", "Usuario"),
        "categorias": list(categorias.keys()),
        "totales": list(categorias.values()),
        "activas": activas,
        "inactivas": inactivas,
        "meses": meses,
        "gastos_mensuales": [gasto_mensual[mes] for mes in meses],
    }

    response = render(request, "menu.html", context)

    # Agregar cabeceras para evitar cache del navegador
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response

@csrf_exempt
def perfil_usuario(request):
    """Vista para mostrar y editar el perfil del usuario"""
    try:
        user_session = request.session.get("user")
        if not user_session:
            return redirect("login")

        uid = user_session.get("uid")
        if not uid:
            return redirect("login")

        # Obtener usuario actual desde Firebase
        usuario = auth.get_user(uid)

        if request.method == 'POST':
            nuevo_nombre = request.POST.get('display_name', '').strip()
            if nuevo_nombre:
                try:
                    # 🔥 Actualiza Firebase Authentication
                    auth.update_user(uid, display_name=nuevo_nombre)

                    # 🔥 Actualiza Firestore
                    db.collection("usuarios").document(uid).update({
                        "nombre": nuevo_nombre
                    })

                    # 🔁 Actualiza la base de datos local
                    usuario_local = UsuarioLocal.objects.get(uid=uid)
                    usuario_local.nombre = nuevo_nombre
                    usuario_local.save()

                    # 🔄 Actualiza la sesión
                    request.session["user"]["nombre"] = nuevo_nombre

                    messages.success(request, "Perfil actualizado correctamente.")

                    # Refrescar objeto usuario con nuevo display_name
                    usuario = auth.get_user(uid)

                except Exception as e:
                    print("Error al actualizar perfil:", e)
                    messages.error(request, "No se pudo actualizar el perfil.")
            else:
                messages.error(request, "El nombre no puede estar vacío.")

        contexto = {
            'usuario': usuario
        }
        return render(request, 'perfil.html', contexto)

    except Exception as e:
        print("Error general en perfil_usuario:", e)
        messages.error(request, "Ocurrió un error al cargar tu perfil.")
        return redirect("menu")