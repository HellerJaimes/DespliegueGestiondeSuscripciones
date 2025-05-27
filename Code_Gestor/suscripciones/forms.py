from django import forms
from .models import Suscripcion, Pago

class SuscripcionForm(forms.ModelForm):
    class Meta:
        model = Suscripcion
        fields = ['servicio', 'costo', 'fecha_pago', 'categoria', 'activo']
        widgets = {
        }

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['suscripcion', 'monto']
        widgets = {
            'monto': forms.NumberInput(attrs={'step': '0.01'}),
        }
