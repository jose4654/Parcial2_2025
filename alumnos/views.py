from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
from .models import Alumno
from .forms import AlumnoForm

@login_required
def dashboard(request):
    """Dashboard principal de alumnos"""
    alumnos = Alumno.objects.filter(usuario=request.user)
    return render(request, 'alumnos/dashboard.html', {'alumnos': alumnos})

@login_required
def crear_alumno(request):
    """Vista para crear un nuevo alumno y enviar PDF automáticamente"""
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.usuario = request.user
            alumno.save()
            
            # Enviar PDF automáticamente al crear el alumno
            try:
                # Validar que el usuario tenga email
                if not request.user.email:
                    messages.warning(request, f'Alumno {alumno.nombre} {alumno.apellido} creado exitosamente, pero no se pudo enviar el PDF porque no tienes correo registrado. Ve a /admin para agregarlo.')
                    return redirect('dashboard')
                
                # Validar que esté configurado el correo (console está permitido para desarrollo)
                if 'filebased' in str(settings.EMAIL_BACKEND):
                    messages.warning(request, 
                        f'Alumno {alumno.nombre} {alumno.apellido} creado exitosamente.\n'
                        '⚠️ Para enviar PDFs automáticamente:\n'
                        '1. Ejecuta: python configurar_correo.py\n'
                        '2. O crea archivo .env con tus credenciales Gmail\n'
                        '3. Reinicia el servidor')
                    return redirect('dashboard')
                
                # Generar PDF
                buffer = BytesIO()
                p = canvas.Canvas(buffer, pagesize=letter)
                width, height = letter
                
                # Título
                p.setFont("Helvetica-Bold", 20)
                p.drawString(100, height - 100, "Información del Alumno")
                
                # Datos del alumno
                y = height - 150
                p.setFont("Helvetica", 12)
                datos = [
                    f"Nombre: {alumno.nombre} {alumno.apellido}",
                    f"Email: {alumno.email}",
                    f"Teléfono: {alumno.telefono or 'No especificado'}",
                    f"Fecha de Nacimiento: {alumno.fecha_nacimiento or 'No especificada'}",
                    f"Dirección: {alumno.direccion or 'No especificada'}",
                    f"Fecha de Registro: {alumno.fecha_creacion.strftime('%d/%m/%Y %H:%M')}",
                ]
                
                for dato in datos:
                    p.drawString(100, y, dato)
                    y -= 30
                
                p.showPage()
                p.save()
                
                # Obtener el PDF
                buffer.seek(0)
                pdf_data = buffer.getvalue()
                buffer.close()
                
                # Validar que el usuario (admin/docente) tenga email
                if not request.user.email:
                    messages.warning(request, f'Alumno {alumno.nombre} {alumno.apellido} creado exitosamente, pero no se pudo enviar el PDF porque no tienes correo registrado. Ve a /admin para agregarlo.')
                else:
                    # Enviar por correo al ADMIN/DOCENTE (usuario logueado)
                    from_email = settings.DEFAULT_FROM_EMAIL if settings.DEFAULT_FROM_EMAIL else settings.EMAIL_HOST_USER
                    email = EmailMessage(
                        f'Información del Alumno: {alumno.nombre} {alumno.apellido}',
                        f'Hola {request.user.username},\n\n'
                        f'Se ha registrado un nuevo alumno: {alumno.nombre} {alumno.apellido}.\n'
                        f'Adjunto encontrarás la información completa del alumno.\n\n'
                        'Saludos,\nSistema Educativo',
                        from_email,
                        [request.user.email],  # Se envía al correo del ADMIN/DOCENTE
                    )
                    email.attach(f'alumno_{alumno.id}_{alumno.nombre}_{alumno.apellido}.pdf', pdf_data, 'application/pdf')
                    email.send()
                    
                    messages.success(request, f'✅ Alumno {alumno.nombre} {alumno.apellido} creado exitosamente. PDF enviado automáticamente a {request.user.email}')
            except Exception as e:
                error_msg = str(e)
                if 'Authentication Required' in error_msg or '530' in error_msg:
                    messages.warning(request, 
                        f'Alumno {alumno.nombre} {alumno.apellido} creado exitosamente.\n'
                        '❌ No se pudo enviar el PDF. Verifica EMAIL_HOST_USER y EMAIL_HOST_PASSWORD en settings.py')
                else:
                    messages.warning(request, f'Alumno creado exitosamente, pero hubo un error al enviar el PDF: {error_msg}')
            
            return redirect('dashboard')
    else:
        form = AlumnoForm()
    return render(request, 'alumnos/crear_alumno.html', {'form': form})

@login_required
def editar_alumno(request, pk):
    """Vista para editar un alumno existente"""
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alumno actualizado exitosamente.')
            return redirect('dashboard')
    else:
        form = AlumnoForm(instance=alumno)
    return render(request, 'alumnos/editar_alumno.html', {'form': form, 'alumno': alumno})

@login_required
def eliminar_alumno(request, pk):
    """Vista para eliminar un alumno"""
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    if request.method == 'POST':
        nombre = f"{alumno.nombre} {alumno.apellido}"
        alumno.delete()
        messages.success(request, f'Alumno {nombre} eliminado exitosamente.')
        return redirect('dashboard')
    return render(request, 'alumnos/eliminar_alumno.html', {'alumno': alumno})

@login_required
def enviar_pdf_alumno(request, pk):
    """Genera un PDF del alumno y lo envía por correo"""
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    # Crear PDF en memoria
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Título
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, height - 100, "Información del Alumno")
    
    # Datos del alumno
    y = height - 150
    p.setFont("Helvetica", 12)
    datos = [
        f"Nombre: {alumno.nombre} {alumno.apellido}",
        f"Email: {alumno.email}",
        f"Teléfono: {alumno.telefono or 'No especificado'}",
        f"Fecha de Nacimiento: {alumno.fecha_nacimiento or 'No especificada'}",
        f"Dirección: {alumno.direccion or 'No especificada'}",
        f"Fecha de Registro: {alumno.fecha_creacion.strftime('%d/%m/%Y %H:%M')}",
    ]
    
    for dato in datos:
        p.drawString(100, y, dato)
        y -= 30
    
    p.showPage()
    p.save()
    
    # Obtener el PDF
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # No bloquear si está en modo console (los correos se mostrarán en los logs)
    
    # Validar que el usuario (admin/docente) tenga email
    if not request.user.email:
        messages.error(request, 'Error: No tienes un correo electrónico registrado. Ve a /admin y agrega tu correo en tu perfil de usuario.')
        return redirect('dashboard')
    
    # Enviar por correo real al ADMIN/DOCENTE (usuario logueado)
    try:
        from_email = settings.DEFAULT_FROM_EMAIL if settings.DEFAULT_FROM_EMAIL else settings.EMAIL_HOST_USER
        email = EmailMessage(
            f'Información del Alumno: {alumno.nombre} {alumno.apellido}',
            f'Hola {request.user.username},\n\n'
            f'Adjunto encontrarás la información del alumno {alumno.nombre} {alumno.apellido}.\n\n'
            'Saludos,\nSistema Educativo',
            from_email,
            [request.user.email],  # Se envía al correo del ADMIN/DOCENTE
        )
        email.attach(f'alumno_{alumno.id}_{alumno.nombre}_{alumno.apellido}.pdf', pdf_data, 'application/pdf')
        email.send()
        
        # Verificar si está en modo console o SMTP real
        if 'console' in str(settings.EMAIL_BACKEND):
            messages.success(request, f'✅ PDF generado exitosamente. El correo se mostrará en la consola del servidor (destinatario: {request.user.email})')
        else:
            messages.success(request, f'✅ PDF enviado exitosamente a {request.user.email}')
    except Exception as e:
        error_msg = str(e)
        if 'Authentication Required' in error_msg or '530' in error_msg:
            messages.error(request, 
                '❌ Error de autenticación Gmail.\n'
                'Verifica en sistema_educativo/settings.py que EMAIL_HOST_USER y EMAIL_HOST_PASSWORD sean correctos.\n'
                'Luego reinicia el servidor.')
        elif '535' in error_msg or 'authentication failed' in error_msg.lower():
            messages.error(request, 
                '❌ Credenciales incorrectas de Gmail.\n'
                'Verifica en sistema_educativo/settings.py que EMAIL_HOST_USER y EMAIL_HOST_PASSWORD sean correctos.')
        else:
            messages.error(request, f'❌ Error al enviar el correo: {error_msg}')
    
    return redirect('dashboard')
