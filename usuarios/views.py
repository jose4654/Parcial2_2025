from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegistroForm

def registro(request):
    """Vista para registro de nuevos usuarios"""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Enviar correo de bienvenida
            if user.email and settings.DEFAULT_FROM_EMAIL:
                try:
                    send_mail(
                        'Bienvenido al Sistema Educativo',
                        f'Hola {user.username},\n\n¡Bienvenido al Sistema Educativo!\n\n'
                        'Tu cuenta ha sido creada exitosamente. Ahora puedes iniciar sesión y comenzar a gestionar tus alumnos.\n\n'
                        'Saludos,\nEquipo del Sistema Educativo',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    messages.success(request, '¡Registro exitoso! Se ha enviado un correo de bienvenida.')
                except Exception as e:
                    messages.warning(request, f'Registro exitoso, pero no se pudo enviar el correo: {str(e)}')
            else:
                if not user.email:
                    messages.warning(request, '¡Registro exitoso! Nota: No se pudo enviar el correo porque no tienes un email registrado.')
                elif not settings.DEFAULT_FROM_EMAIL:
                    messages.warning(request, '¡Registro exitoso! Nota: No se pudo enviar el correo porque el sistema no tiene configurado el correo remitente.')
            
            # Autenticar y redirigir
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})
