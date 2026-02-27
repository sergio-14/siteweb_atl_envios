from django import forms
from .models import Paquete

class PaqueteForm(forms.ModelForm):
    class Meta:
        model = Paquete
        # Añadimos 'origen' y 'destino' a la lista de campos
        fields = [
            'descripcion', 'peso', 'dimensiones', 'cliente', 
            'imagen', 'origen', 'destino', 'direccion_destino', 
            'fecha_envio', 'precio'
        ]
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'dimensiones': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            
            # Origen: Se muestra pero no se puede editar (readonly)
            'origen': forms.TextInput(attrs={
                'class': 'form-control', 
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef;' # Color grisáceo para indicar que es fijo
            }),
            
            # Destino: Ciudad o sucursal donde llega
            'destino': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Sucursal Central Santa Cruz'
            }),
            
            'direccion_destino': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección exacta de entrega'
            }),
            
            'fecha_envio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
        }