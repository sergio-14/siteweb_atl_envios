from django import forms
from .models import Paquete

class PaqueteForm(forms.ModelForm):
    class Meta:
        model = Paquete
        fields = ['descripcion', 'peso', 'dimensiones', 'cliente', 'imagen', 'direccion_destino' ,'fecha_envio','precio']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'dimensiones': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'direccion_destino': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_envio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
        }
