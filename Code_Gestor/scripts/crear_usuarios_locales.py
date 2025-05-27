import firebase_admin
from firebase_admin import credentials, auth
from suscripciones.models import UsuarioLocal
from django.conf import settings
# Inicializa Firebase (usa tu credencial privada)
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
# Listar todos los usuarios
from main.models import Suscripcion, UsuarioLocal

# Recorremos todas las suscripciones que no tienen usuario_local asignado
suscripciones_sin_usuario = Suscripcion.objects.filter(usuario_local__isnull=True)

for suscripcion in suscripciones_sin_usuario:
    # Buscamos el UsuarioLocal correspondiente al uid de la suscripción
    usuario_local = UsuarioLocal.objects.get(uid=suscripcion.uid_firebase)  # Suponiendo que la suscripción tiene el campo `uid_firebase`
    
    # Asignamos el UsuarioLocal a la suscripción
    suscripcion.usuario_local = usuario_local
    suscripcion.save()

print("Suscripciones actualizadas correctamente.")