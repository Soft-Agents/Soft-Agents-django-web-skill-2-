from pathlib import Path
import os
import sys
import traceback
from decouple import config

# LOGGING TEMPRANO PARA CAPTURAR ERRORES DE INICIO
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s %(asctime)s %(module)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("INICIANDO CARGA DE SETTINGS.PY")
logger.info("=" * 80)

try:
    # Build paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    logger.info(f"✅ BASE_DIR: {BASE_DIR}")

    # DEBUG debe ser booleano
    DEBUG = config('DEBUG', default=False, cast=bool)
    logger.info(f"✅ DEBUG: {DEBUG}")

    # Secret Key
    SECRET_KEY = config('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("❌ SECRET_KEY no configurado en variables de entorno")
    logger.info(f"✅ SECRET_KEY: {SECRET_KEY[:10]}...")

    # Configuración de seguridad
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True

    # Hosts permitidos
    allowed_hosts_env = os.getenv('ALLOWED_HOSTS_PROD', '')
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '.run.app', '.googleapis.com'])
    logger.info(f"✅ ALLOWED_HOSTS: {ALLOWED_HOSTS}")

    # Aplicaciones
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        'web_skill_app',
        'theme',
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "web_skill.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    'web_skill_app.context_processors.user_context',
                ],
            },
        },
    ]

    WSGI_APPLICATION = "web_skill.wsgi.application"
    logger.info(f"✅ WSGI_APPLICATION: {WSGI_APPLICATION}")

    # Base de datos
    MONGO_URI = config('MONGO_URI')
    if not MONGO_URI:
        raise ValueError("❌ MONGO_URI no configurado")
    logger.info(f"✅ MONGO_URI: {MONGO_URI[:30]}...")

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    logger.info(f"✅ DATABASES configurado")

    # Validación de contraseñas
    AUTH_PASSWORD_VALIDATORS = [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    # Internacionalización
    LANGUAGE_CODE = "es-pe"
    TIME_ZONE = "America/Lima"
    USE_I18N = True
    USE_TZ = True

    # Archivos estáticos
    STATIC_URL = "static/"
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [
        BASE_DIR / 'web_skill_app' / 'static',
        BASE_DIR / 'theme' / 'static',
    ]
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
    logger.info(f"✅ STATIC_ROOT: {STATIC_ROOT}")

    # CSRF
    CSRF_TRUSTED_ORIGINS = ['https://*.run.app', 'https://*.googleapis.com']
    csrf_origins_env = os.getenv('ALLOWED_HOSTS_PROD', '')
    if csrf_origins_env:
        for host in csrf_origins_env.split(','):
            host = host.strip()
            if host:
                CSRF_TRUSTED_ORIGINS.append(f'https://{host}')
    
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_HTTPONLY = False
    CSRF_USE_SESSIONS = False
    CSRF_COOKIE_AGE = 31449600
    logger.info(f"✅ CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")

    # Caché
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'verbose',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }

    # MongoDB
    MONGO_DB_NAME = config('MONGO_DB_NAME', default='webSkill')
    logger.info(f"✅ MONGO_DB_NAME: {MONGO_DB_NAME}")

    # URLs de agentes (CORREGIDO: Usando config en vez de os.getenv)
    AGENT_PROFESOR = config('AGENT_PROFESOR', default='')
    AGENT_CRIKER_COACH = config('AGENT_CRIKER_COACH', default='')
    AGENT_CRIKER_SKILL = config('AGENT_CRIKER_SKILL', default='')
    SOFIA_AGENT_URL = config('SOFIA_AGENT_URL', default='')
    AGENT_ENCUESTA_URL = config('AGENT_ENCUESTA_URL', default='')
    AGENT_SCOUTER_URL = config('AGENT_SCOUTER_URL', default='')
    STREAMLIT_SERVER_URL = config('STREAMLIT_SERVER_URL', default='http://localhost:8501')

    logger.info("=" * 80)
    logger.info("✅ SETTINGS.PY CARGADO EXITOSAMENTE")
    logger.info("=" * 80)

except Exception as e:
    logger.error("=" * 80)
    logger.error("❌ ERROR FATAL AL CARGAR SETTINGS.PY")
    logger.error("=" * 80)
    logger.error(traceback.format_exc())
    raise