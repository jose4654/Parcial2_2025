# Sistema Educativo - Django

Sistema completo de gestión educativa con autenticación, gestión de alumnos, generación de PDFs y scraping educativo.

## Características

- 🔐 **Autenticación**: Registro y login de usuarios con envío de correo de bienvenida
- 🧑‍🎓 **Gestión de Alumnos**: CRUD completo de alumnos con dashboard
- 📄 **Generación de PDFs**: Creación y envío de PDFs con información de alumnos
- 🔎 **Scraping Educativo**: Búsqueda de contenido en Wikipedia
- ☁️ **Deploy en Render**: Configurado para producción

## Requisitos

- Python 3.14+
- Django 5.2.8
- Virtual environment

## Instalación Local

1. Clonar el repositorio
2. Crear y activar entorno virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Realizar migraciones:
```bash
python manage.py migrate
```

5. Crear superusuario:
```bash
python manage.py createsuperuser
```

6. Ejecutar servidor:
```bash
python manage.py runserver
```

## Configuración de Correo

**Para desarrollo local:**
- Por defecto, los correos se mostrarán en la consola del servidor (útil para pruebas)
- Para enviar correos reales, configura las variables de entorno en `sistema_educativo/settings.py`

**Para Gmail:**
1. Activa verificación en 2 pasos en tu cuenta de Google
2. Genera una "Contraseña de aplicación" en: https://myaccount.google.com/apppasswords
3. Configura las variables de entorno (ver sección Deploy en Render para producción)

## Deploy en Render

### Opción 1: Usando render.yaml (Recomendado)
1. Conectar tu repositorio en Render
2. Render detectará automáticamente el archivo `render.yaml`
3. Configurar las variables de entorno en el dashboard de Render:
   - `EMAIL_HOST`: smtp.gmail.com (o tu servidor SMTP)
   - `EMAIL_PORT`: 587
   - `EMAIL_USE_TLS`: True
   - `EMAIL_HOST_USER`: Tu correo electrónico
   - `EMAIL_HOST_PASSWORD`: Tu contraseña de aplicación
   - `DEFAULT_FROM_EMAIL`: Tu correo electrónico
   - `SECRET_KEY`: Se genera automáticamente
   - `DEBUG`: False (para producción)

### Opción 2: Configuración Manual
1. Conectar repositorio en Render
2. Configurar:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn sistema_educativo.wsgi:application`
   - **Python Version**: 3.11.0 (según runtime.txt)
3. Configurar variables de entorno (ver arriba)

## Estructura del Proyecto

- `usuarios/`: App de autenticación
- `alumnos/`: App de gestión de alumnos
- `scraping/`: App de búsqueda de contenido
- `templates/`: Templates HTML con Bootstrap
- `static/`: Archivos estáticos

## Tecnologías

- Django 5.2.8
- Bootstrap 5.3
- ReportLab (PDFs)
- BeautifulSoup4 (Scraping)
- WhiteNoise (Archivos estáticos)
- Gunicorn (Servidor WSGI)

