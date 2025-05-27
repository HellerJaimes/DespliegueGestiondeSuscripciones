from firebase_admin import auth
from django.http import JsonResponse
from .models import Usuario

def firebase_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        id_token = request.headers.get('Authorization')
        
        if not id_token:
            return JsonResponse({'error': 'Token no encontrado'}, status=401)

        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            nombre = decoded_token.get('name')

            # Crea o actualiza el usuario local
            usuario, creado = Usuario.objects.get_or_create(uid=uid)
            if email:
                usuario.email = email
            if nombre:
                usuario.nombre = nombre
            usuario.save()

            # Guarda el usuario en el request para usarlo después
            request.usuario_firebase = usuario

        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Token inválido'}, status=401)

        return view_func(request, *args, **kwargs)
    return wrapper