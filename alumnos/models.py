from django.db import models
from django.contrib.auth.models import User

class Alumno(models.Model):
    """Modelo para almacenar información de alumnos"""
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    email = models.EmailField(verbose_name='Correo Electrónico')
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento', null=True, blank=True)
    telefono = models.CharField(max_length=20, verbose_name='Teléfono', null=True, blank=True)
    direccion = models.TextField(verbose_name='Dirección', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    
    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
