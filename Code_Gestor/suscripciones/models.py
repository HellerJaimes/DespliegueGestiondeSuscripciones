from django.db import models
from django.utils.timezone import now
from main.models import UsuarioLocal
from django.utils import timezone


class Suscripcion(models.Model):
    categorias = [
        ('Entretenimiento', 'Entretenimiento'),
        ('Música', 'Música'),
        ('Educación', 'Educación'),
        ('Otros', 'Otros'),
    ]

    usuario_local = models.ForeignKey(UsuarioLocal, on_delete=models.CASCADE, default=1) # 👈 Aquí usas el usuario real
    servicio = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    fecha_pago = models.DateField(default=now)
    categoria = models.CharField(max_length=20, choices=categorias, default='Otros')
    activo = models.BooleanField(default=True)  # Indica si la suscripción está activa

    meses = models.PositiveIntegerField(default=1)  # Contará los meses de la suscripción activa.
    total_gastado = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total gastado hasta la fecha.
    ultima_actualizacion = models.DateField(default=timezone.now)
    
    def actualizar_mes(self):
        """Función para actualizar el número de mes y el total gastado."""
        self.meses += 1  # Aumenta el mes
        self.total_gastado += self.costo  # Suma el costo de la suscripción al total gastado
        self.save()
        
    def __str__(self):
        return f"{self.servicio} - {self.costo} USD - {self.categoria}"

class Pago(models.Model):
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE, related_name="pagos")
    fecha_pago = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Pago de {self.monto} USD para {self.suscripcion.servicio} el {self.fecha_pago}"

class Notificacion(models.Model):
    uid = models.CharField(max_length=255)  # UID de Firebase del usuario destinatario
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.uid}: {'Leída' if self.leida else 'No Leída'}"
    

