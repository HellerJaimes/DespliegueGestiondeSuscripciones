from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Suscripcion, UsuarioLocal
from .forms import SuscripcionForm
from django.contrib import messages
from datetime import date
from dateutil.relativedelta import relativedelta  # Asegúrate de instalarlo: pip install python-dateutil
from django.db.models import F
from django.db.models import Sum
from django.views.decorators.cache import never_cache

@never_cache
def dashboard(request):
    user_session = request.session.get("user")  # Obtener el usuario de la sesión
    if not user_session:
        return redirect("login")  # Redirigir si no hay sesión

    # Obtener el UsuarioLocal asociado al usuario en sesión
    try:
        usuario_local = UsuarioLocal.objects.get(uid=user_session.get("uid"))
    except UsuarioLocal.DoesNotExist:
        usuario_local = None

    if not usuario_local:
        return redirect("login")  # Redirigir si no se encuentra el usuario local

    # Filtrar suscripciones por el usuario_local
    categoria_filtro = request.GET.get("categoria")  # Obtiene la categoría del filtro si existe
    estado_filtro = request.GET.get("estado")  # Obtiene el estado del filtro si existe

    suscripciones = Suscripcion.objects.filter(usuario_local=usuario_local)

    if categoria_filtro:
        suscripciones = suscripciones.filter(categoria=categoria_filtro)

    if estado_filtro == 'activo':
        suscripciones = suscripciones.filter(activo=True)
    elif estado_filtro == 'inactivo':
        suscripciones = suscripciones.filter(activo=False)

    # Actualizar automáticamente meses y total_gastado para suscripciones vencidas
    for suscripcion in suscripciones:
        if suscripcion.activo and suscripcion.fecha_pago <= date.today():
            meses_transcurridos = 0
            fecha_actual = suscripcion.fecha_pago

            while fecha_actual <= date.today():
                meses_transcurridos += 1
                fecha_actual += relativedelta(months=1)

            # Solo guarda si hubo cambios
            if meses_transcurridos > 0:
                suscripcion.meses += meses_transcurridos
                suscripcion.total_gastado += suscripcion.costo * meses_transcurridos
                suscripcion.fecha_pago = fecha_actual
                suscripcion.save()

    # Mejorar el rendimiento guardando solo una vez al día
    for suscripcion in suscripciones:
        if not suscripcion.ultima_actualizacion or suscripcion.ultima_actualizacion < date.today():
            if suscripcion.activo:
                # Lógica de actualización de meses y total_gastado
                meses_transcurridos = 0
                fecha_actual = suscripcion.fecha_pago

                while fecha_actual <= date.today():
                    meses_transcurridos += 1
                    fecha_actual += relativedelta(months=1)

                # Solo guarda si hubo cambios
                if meses_transcurridos > 0:
                    suscripcion.meses += meses_transcurridos
                    suscripcion.total_gastado += suscripcion.costo * meses_transcurridos
                    suscripcion.fecha_pago = fecha_actual
                    suscripcion.ultima_actualizacion = date.today()
                    suscripcion.save()

    categorias = Suscripcion._meta.get_field("categoria").choices

    form = SuscripcionForm()

    # Estadísticas adicionales
    total_gastado_por_categoria = {
        categoria: Suscripcion.objects.filter(usuario_local=usuario_local, categoria=categoria).aggregate(total=Sum('total_gastado'))['total'] or 0
        for categoria, _ in categorias
    }

    contexto = {
        "nombre": user_session.get("nombre", "Usuario"),
        "total_suscripciones": suscripciones.count(),
        "total_gastado_por_categoria": total_gastado_por_categoria,
        "suscripciones": suscripciones,
        "categorias": categorias,
        "form": form,
    }

    response = render(request, "dashboard.html", contexto)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def agregar_suscripcion(request):
    user_session = request.session.get("user")
    if not user_session:
        return redirect("login")  # Redirigir si no hay sesión

    if request.method == "POST":
        # Obtener el UsuarioLocal
        try:
            usuario_local = UsuarioLocal.objects.get(uid=user_session.get("uid"))
        except UsuarioLocal.DoesNotExist:
            usuario_local = None

        if usuario_local:
            servicio = request.POST.get("servicio")
            costo = request.POST.get("costo")
            fecha_pago = request.POST.get("fecha_pago")
            categoria = request.POST.get("categoria")

            Suscripcion.objects.create(
                usuario_local=usuario_local,  # Asignamos el UsuarioLocal
                servicio=servicio,
                costo=costo,
                fecha_pago=fecha_pago,
                categoria=categoria,
                activo=True
            )
            messages.success(request, "✅ Suscripción agregada exitosamente.")

        return redirect("suscripciones_dashboard")


def eliminar_suscripcion(request, suscripcion_id):
    user_session = request.session.get("user")
    if not user_session:
        return redirect("login")

    try:
        usuario_local = UsuarioLocal.objects.get(uid=user_session.get("uid"))
    except UsuarioLocal.DoesNotExist:
        usuario_local = None

    if usuario_local:
        suscripcion = Suscripcion.objects.get(id=suscripcion_id, usuario_local=usuario_local)
        suscripcion.delete()
        messages.success(request, "🗑️ Suscripción eliminada correctamente.")
    return redirect("suscripciones_dashboard")


def obtener_suscripciones(request):
    user_session = request.session.get("user")
    if not user_session:
        return JsonResponse({"error": "No autenticado"}, status=401)

    try:
        usuario_local = UsuarioLocal.objects.get(uid=user_session.get("uid"))
    except UsuarioLocal.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

    suscripciones = list(Suscripcion.objects.filter(usuario_local=usuario_local).values())
    return JsonResponse({"suscripciones": suscripciones})


def editar_suscripcion(request, suscripcion_id):
    user_session = request.session.get("user")
    if not user_session:
        return redirect("login")

    try:
        usuario_local = UsuarioLocal.objects.get(uid=user_session.get("uid"))
    except UsuarioLocal.DoesNotExist:
        return redirect("login")

    suscripcion = get_object_or_404(Suscripcion, id=suscripcion_id, usuario_local=usuario_local)

    if request.method == "POST":
        # Obtener datos del formulario
        suscripcion.servicio = request.POST.get("servicio")
        suscripcion.costo = request.POST.get("costo")
        suscripcion.fecha_pago = request.POST.get("fecha_pago")
        suscripcion.categoria = request.POST.get("categoria")

        activo = request.POST.get("activo") == 'on'  # Si el checkbox está marcado, será 'on'

        # Actualizar el estado activo
        suscripcion.activo = activo

        # Guardar los cambios
        suscripcion.save()
        messages.success(request, "Suscripción actualizada correctamente.")
        return redirect("suscripciones_dashboard")

    return redirect("suscripciones_dashboard")
