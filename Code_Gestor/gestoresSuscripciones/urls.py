from django.contrib import admin
from django.urls import path, include
from main import views as main_views
from django.contrib.auth.views import LoginView

from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),  # Redirige a main
    path('suscripciones/', include('suscripciones.urls')),  # Redirige a suscripciones
]
