from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from bs4 import BeautifulSoup
import requests
from .forms import BusquedaForm

@login_required
def buscar_contenido(request):
    """Vista para realizar scraping educativo"""
    resultados = []
    
    if request.method == 'POST':
        form = BusquedaForm(request.POST)
        if form.is_valid():
            palabra_clave = form.cleaned_data['palabra_clave']
            
            # Realizar scraping en Wikipedia (ejemplo educativo)
            try:
                url = f"https://es.wikipedia.org/wiki/{palabra_clave.replace(' ', '_')}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extraer título
                    titulo = soup.find('h1', class_='firstHeading')
                    titulo_texto = titulo.text if titulo else 'No encontrado'
                    
                    # Extraer párrafos principales
                    contenido = soup.find('div', class_='mw-parser-output')
                    parrafos = []
                    if contenido:
                        for p in contenido.find_all('p', limit=5):
                            texto = p.get_text().strip()
                            if texto and len(texto) > 50:
                                parrafos.append(texto)
                    
                    resultados.append({
                        'titulo': titulo_texto,
                        'url': url,
                        'parrafos': parrafos[:3],  # Primeros 3 párrafos
                        'palabra_clave': palabra_clave
                    })
                    
                    messages.success(request, f'Búsqueda realizada exitosamente para: {palabra_clave}')
                else:
                    messages.warning(request, 'No se encontraron resultados en Wikipedia. Intenta con otra palabra clave.')
                    
            except Exception as e:
                messages.error(request, f'Error al realizar la búsqueda: {str(e)}')
    else:
        form = BusquedaForm()
    
    return render(request, 'scraping/buscar.html', {
        'form': form,
        'resultados': resultados
    })

@login_required
def enviar_resultados(request):
    """Envía los resultados del scraping por correo"""
    if request.method == 'POST':
        palabra_clave = request.POST.get('palabra_clave')
        titulo = request.POST.get('titulo')
        url = request.POST.get('url')
        parrafos = request.POST.getlist('parrafos')
        
        # Construir contenido del correo
        contenido = f"Resultados de búsqueda para: {palabra_clave}\n\n"
        contenido += f"Título: {titulo}\n"
        contenido += f"URL: {url}\n\n"
        contenido += "Contenido encontrado:\n"
        contenido += "-" * 50 + "\n"
        for i, parrafo in enumerate(parrafos, 1):
            contenido += f"\n{i}. {parrafo}\n"
        
        # Validar que el usuario tenga email
        if not request.user.email:
            messages.error(request, 'Error: No tienes un correo electrónico registrado. Ve a /admin y agrega tu correo en tu perfil de usuario.')
            return redirect('buscar_contenido')
        
        # Validar que esté configurado el correo (console está permitido para desarrollo)
        if 'filebased' in str(settings.EMAIL_BACKEND):
            messages.error(request, 
                '⚠️ Correo no configurado. Para enviar correos reales:\n'
                '1. Abre sistema_educativo/settings.py\n'
                '2. Configura EMAIL_BACKEND (puede ser console para desarrollo o smtp para producción)\n'
                '3. Reinicia el servidor')
            return redirect('buscar_contenido')
        
        try:
            from_email = settings.DEFAULT_FROM_EMAIL if settings.DEFAULT_FROM_EMAIL else settings.EMAIL_HOST_USER
            email = EmailMessage(
                f'Resultados de búsqueda: {palabra_clave}',
                contenido,
                from_email,
                [request.user.email],
            )
            email.send()
            messages.success(request, f'✅ Resultados enviados exitosamente a {request.user.email}')
        except Exception as e:
            error_msg = str(e)
            if 'Authentication Required' in error_msg or '530' in error_msg:
                messages.error(request, 
                    '❌ Error de autenticación Gmail.\n'
                    'Configura en settings.py:\n'
                    'TU_CORREO_GMAIL = "tu-correo@gmail.com"\n'
                    'TU_CONTRASEÑA_APLICACION = "tu-contraseña-de-16-caracteres"')
            elif '535' in error_msg or 'authentication failed' in error_msg.lower():
                messages.error(request, '❌ Credenciales incorrectas. Verifica TU_CORREO_GMAIL y TU_CONTRASEÑA_APLICACION en settings.py')
            else:
                messages.error(request, f'❌ Error al enviar el correo: {error_msg}')
    
    return redirect('buscar_contenido')
