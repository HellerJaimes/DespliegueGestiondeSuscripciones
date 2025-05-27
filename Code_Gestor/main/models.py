from django.db import models

# Create your models here.
class UsuarioLocal(models.Model):
    uid = models.CharField(max_length=100, unique=True)  # UID de Firebase
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.email