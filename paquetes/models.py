from django.contrib.auth.models import User
from django.db import models

# Modelo Cliente relacionado con User
class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente_profile')  
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return self.user.get_full_name()  


# Modelo Empleado relacionado con User
class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleado_profile')  
    cargo = models.CharField(max_length=50) 
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.cargo}"  


# Modelo EstadoPaquete
class EstadoPaquete(models.Model):
    nombre_estado = models.CharField(max_length=50)  

    def __str__(self):
        return self.nombre_estado



# Modelo HistorialEstadoPaquete
class HistorialEstadoPaquete(models.Model):
    paquete = models.ForeignKey('Paquete', on_delete=models.CASCADE, related_name='historial_estados')
    estado = models.ForeignKey('EstadoPaquete', on_delete=models.CASCADE)
    fecha_cambio = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Paquete: {self.paquete.descripcion} - Estado: {self.estado.nombre_estado}"



# Modelo Paquete envio  
class Paquete(models.Model):
    descripcion = models.CharField(max_length=255)
    peso = models.FloatField()  
    dimensiones = models.CharField(max_length=50)  
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='paquetes')
    imagen = models.ImageField(upload_to='paquetes/', null=True, blank=True)  
    direccion_destino = models.CharField(max_length=255)  
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE)
    fecha_envio = models.DateTimeField()
    estado = models.ForeignKey('EstadoPaquete', on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.descripcion} - Cliente: {self.cliente.user.get_full_name()}"
