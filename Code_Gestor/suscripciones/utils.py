from django.utils.timezone import now
from .models import Suscripcion

def verificar_y_actualizar_suscripciones():
    hoy = now().date()
    suscripciones = Suscripcion.objects.filter(activo=True)

    for sus in suscripciones:
        if sus.fecha_pago <= hoy:
            sus.actualizar_mes()
            # Mover la fecha de pago al siguiente mes
            try:
                nuevo_mes = sus.fecha_pago.month + 1
                nuevo_anio = sus.fecha_pago.year
                if nuevo_mes > 12:
                    nuevo_mes = 1
                    nuevo_anio += 1
                sus.fecha_pago = sus.fecha_pago.replace(year=nuevo_anio, month=nuevo_mes)
            except ValueError:
                # Por si el día no existe (ejemplo: 31 de febrero)
                sus.fecha_pago = sus.fecha_pago.replace(year=nuevo_anio, month=nuevo_mes, day=28)
            sus.save()