from django.urls import path
from . import views

urlpatterns = [
    path('buscar/', views.buscar_contenido, name='buscar_contenido'),
    path('enviar-resultados/', views.enviar_resultados, name='enviar_resultados'),
]

