"""
Settings de PRODUCCIÓN — Sistema de Tickets.

Uso:
    DJANGO_SETTINGS_MODULE=core.settings_prod

Este archivo importa todo desde settings.py (desarrollo) y sobreescribe
solo lo necesario para producción.
"""

import os
from pathlib import Path
from .settings import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Cargar variables de entorno desde .env (si existe)
# ---------------------------------------------------------------------------
from dotenv import load_dotenv

load_dotenv(BASE_DIR / '.env')

# ---------------------------------------------------------------------------
# Seguridad
# ---------------------------------------------------------------------------
DEBUG = False

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# ---------------------------------------------------------------------------
# Base de Datos — PostgreSQL
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'tickets_db'),
        'USER': os.environ.get('DB_USER', 'tickets_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 5,
        },
    }
}

# ---------------------------------------------------------------------------
# Archivos estáticos — WhiteNoise
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', BASE_DIR / 'staticfiles')

# Insertar WhiteNoise justo después de SecurityMiddleware
MIDDLEWARE = [MIDDLEWARE[0], 'whitenoise.middleware.WhiteNoiseMiddleware'] + MIDDLEWARE[1:]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# Archivos multimedia
# ---------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', BASE_DIR / 'media')

# ---------------------------------------------------------------------------
# Eliminar apps y middleware de desarrollo
# ---------------------------------------------------------------------------
_DEV_APPS = {'django_browser_reload', 'tailwind'}
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in _DEV_APPS]

_DEV_MIDDLEWARE = {'django_browser_reload.middleware.BrowserReloadMiddleware'}
MIDDLEWARE = [mw for mw in MIDDLEWARE if mw not in _DEV_MIDDLEWARE]

# ---------------------------------------------------------------------------
# Seguridad HTTP (sin SSL porque aún no hay dominio/certificado)
# ---------------------------------------------------------------------------
# Cuando configures SSL, descomenta las siguientes líneas:
# SECURE_SSL_REDIRECT = True
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
Path(BASE_DIR / 'logs').mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Quitar NPM_BIN_PATH (no se necesita en producción)
# ---------------------------------------------------------------------------
NPM_BIN_PATH = None
