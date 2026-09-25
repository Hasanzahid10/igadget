import os
import environ
from datetime import timedelta

# Initialize environment variables using django-environ
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Read .env file from project root
env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY CRITICAL: Secret key pulled directly from environment
SECRET_KEY = env('SECRET_KEY')

# Toggle DEBUG status from environment (Defaults to False)
DEBUG = env('DEBUG')

# Set domain access rules
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# CORS & CSRF Configuration
CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=True)
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://igadgets.online',
    'https://www.igadgets.online',
    'https://admin.igadgets.online',
    'https://api.igadgets.online',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:5174',
    'http://127.0.0.1:5174',
])

# Application definition

INSTALLED_APPS = [
    # Cloudinary Storage Apps (Must precede django.contrib.staticfiles)
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # Third-party apps
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',

    # Local apps
    'users',
    'catalog',
    'cart',
    'content',
    'orders',
    'wishlist',
    'admin_panel',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be at the very top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Cleaned duplicate entry
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

AUTH_USER_MODEL = 'users.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

# JWT Authentication Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
}

import socket
import subprocess

def _is_postgres_available(host='localhost', port=5432):
    for h in [host, '127.0.0.1']:
        try:
            with socket.create_connection((h, int(port)), timeout=0.5):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass
    
    data_dir = r"C:\my_install\pgsql\data"
    postgres_bin = r"C:\my_install\pgsql\bin\postgres.exe"
    pg_ctl_bin = r"C:\my_install\pgsql\bin\pg_ctl.exe"
    if os.path.exists(postgres_bin) and os.path.exists(data_dir):
        pid_file = os.path.join(data_dir, 'postmaster.pid')
        status_res = subprocess.run([pg_ctl_bin, 'status', '-D', data_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if status_res.returncode != 0 and os.path.exists(pid_file):
            try:
                os.remove(pid_file)
            except Exception:
                pass
        try:
            subprocess.Popen([postgres_bin, "-D", data_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import time
            for _ in range(15):
                for h in [host, '127.0.0.1']:
                    try:
                        with socket.create_connection((h, int(port)), timeout=0.3):
                            return True
                    except (socket.timeout, ConnectionRefusedError, OSError):
                        pass
                time.sleep(0.2)
        except Exception:
            pass

    return False

db_host = env('DB_HOST', default='localhost')
db_port = env('DB_PORT', default='5432')
postgres_url = env('DATABASE_URL', default='')
force_postgres = env.bool('FORCE_POSTGRES', default=not DEBUG)

if postgres_url:
    DATABASES = {
        'default': env.db('DATABASE_URL')
    }
elif force_postgres or (env('DB_ENGINE', default='').endswith('postgresql') and _is_postgres_available(db_host, db_port)):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='igadget_db'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': env('DB_PASSWORD', default='postgres'),
            'HOST': db_host,
            'PORT': db_port,
        }
    }
else:
    if not DEBUG:
        raise RuntimeError("PostgreSQL database is required in Production mode (DEBUG=False). Please set DATABASE_URL or DB_NAME/DB_USER/DB_PASSWORD.")
    print("[NOTICE] PostgreSQL server is not reachable on port 5432. Falling back to local SQLite database for development.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static & Media Files Configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Only include STATICFILES_DIRS if local static directory exists
local_static = os.path.join(BASE_DIR, 'static')
if os.path.exists(local_static):
    STATICFILES_DIRS = [local_static]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Cloudinary Media Storage Configuration (Active ONLY in Live/Production mode)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': env('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
}

use_cloudinary = env.bool('USE_CLOUDINARY', default=not DEBUG)
if use_cloudinary and env('CLOUDINARY_CLOUD_NAME', default=''):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# Production Security Configurations (Enforced when DEBUG=False)
# ==============================================================================
if not DEBUG:
    # Redirect HTTP traffic to HTTPS
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)

    # HTTP Strict Transport Security (HSTS) - 1 Year duration
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Cookie security settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # XSS & Content-Type Protection
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Trust Reverse Proxy SSL Headers (Nginx / Gunicorn)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')