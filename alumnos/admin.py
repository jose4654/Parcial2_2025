from django.contrib import admin
from .models import Alumno

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'email', 'usuario', 'fecha_creacion']
    list_filter = ['fecha_creacion', 'usuario']
    search_fields = ['nombre', 'apellido', 'email']
    readonly_fields = ['fecha_creacion']
