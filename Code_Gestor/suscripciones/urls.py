from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='suscripciones_dashboard'),
    path('agregar/', views.agregar_suscripcion, name='agregar_suscripcion'),
    path('eliminar/<int:suscripcion_id>/', views.eliminar_suscripcion, name='eliminar_suscripcion'),
    path('obtener/', views.obtener_suscripciones, name='obtener_suscripciones'),
    path('editar/<int:suscripcion_id>/', views.editar_suscripcion, name='editar_suscripcion'),
    
]