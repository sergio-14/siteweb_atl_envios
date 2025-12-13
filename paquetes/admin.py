from django.contrib import admin
from .models import Paquete,Cliente,Empleado,HistorialEstadoPaquete,EstadoPaquete
# Register your models here.

admin.site.register(Paquete)
admin.site.register(Empleado)
admin.site.register(Cliente)
admin.site.register(EstadoPaquete)

