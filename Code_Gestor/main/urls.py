from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.home, name="home"),
    path('signup/', views.signup, name="signup"),
    path('login/', views.login_view, name='login'),  # Vista del formulario de login
    path('logout/', views.logout_view, name='logout'),  # Vista para cerrar sesión
    path('quienessomos/', views.quienessomos, name="quienessomos"),
    path('menu/', views.menu, name='menu'),
    path('perfil/', views.perfil_usuario, name='perfil'),
]