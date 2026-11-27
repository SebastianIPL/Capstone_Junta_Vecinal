
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Detecta si se está utilizando la base de datos de Docker.
USING_POSTGRES = bool(os.environ.get("POSTGRES_HOST"))

# Seguridad y configuración general.
# La clave de Docker se obtiene del archivo .env.
# La clave de respaldo solo se utiliza para desarrollo local con SQLite.
SECRET_KEY = os.environ.get("SECRET_KEY") or (
    "django-insecure-sut-local-development-only-change-before-deployment"
    if not USING_POSTGRES else ""
)

DEBUG = os.environ.get(
    "DEBUG",
    "False" if USING_POSTGRES else "True"
).lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1"
    ).split(",")
    if host.strip()
]

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librerías de terceros
    'rest_framework',

    # Módulos del Sistema Unidad Territorial
    'residents',
    'certificates',
    'spaces',
    'projects',
    'bulletins',
    'portal',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Archivos estáticos con WhiteNoise
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Plantillas HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Base de datos
# PostgreSQL en Docker; SQLite para desarrollo local.
if USING_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'sut_db'),
            'USER': os.environ.get('POSTGRES_USER', 'sut_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Validadores de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator'
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'residents.Resident'

# Configuración regional
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND':
        'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Archivos subidos por los usuarios
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Autenticación y navegación
LOGIN_URL = 'portal:login'
LOGIN_REDIRECT_URL = 'portal:dashboard'
LOGOUT_REDIRECT_URL = 'portal:login'

# Certificados
CERTIFICATE_SIGNER_NAME = "Nombre de la persona autorizada"
CERTIFICATE_SIGNER_ROLE = "Presidente/a de la Junta de Vecinos"
