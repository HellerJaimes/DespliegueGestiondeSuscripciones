from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs de la app gestoressubscripciones
    path('', include('gestoressubscripciones.urls')),

    # URLs de la app suscripciones
    path('suscripciones/', include('suscripciones.urls')),
]
