import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
try:
    load_dotenv(BASE_DIR / '.env', encoding='utf-8')
except Exception:
    pass

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-glory-furniture-hub-luxury-solid-teak-key')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://*.trycloudflare.com',
    'https://*.loca.lt',
    'https://*.ngrok-free.app',
    'https://*.hf.space',
    'https://*.huggingface.co',
    'https://*.onrender.com',
    'https://*.koyeb.app',
]

# Allow iframe sessions & CSRF across Hugging Face Space embeds on mobile & desktop
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_AGE = 31536000  # 1 year
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_PATH = '/'

# Cloudinary Media Configuration
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')

if CLOUDINARY_URL:
    if CLOUDINARY_URL.startswith('CLOUDINARY_URL='):
        CLOUDINARY_URL = CLOUDINARY_URL.split('=', 1)[1].strip()
    if '<' in CLOUDINARY_URL or '>' in CLOUDINARY_URL:
        CLOUDINARY_URL = None

if CLOUDINARY_CLOUD_NAME and ('<' in CLOUDINARY_CLOUD_NAME or CLOUDINARY_CLOUD_NAME == 'Glory'):
    # Fix cloud name if set to display name instead of account identifier
    CLOUDINARY_CLOUD_NAME = 'dskull48t'

USE_CLOUDINARY = bool(CLOUDINARY_URL or (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET))

# Application definition
INSTALLED_APPS = [
    *(['cloudinary_storage'] if USE_CLOUDINARY else []),
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    *(['cloudinary'] if USE_CLOUDINARY else []),
    
    # Custom Apps
    'apps.core',
    'apps.store',
    'apps.bookings',
    'apps.custom_orders',
    'apps.accounts',
    'apps.payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'apps.core.middleware.SecurityAndPermissionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware', # Disabled to allow Hugging Face Space iframe
    'apps.accounts.middleware.RoleBasedAccessMiddleware',
]

ROOT_URLCONF = 'glory_furniture.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.global_furniture_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'glory_furniture.wsgi.application'

from django.core.exceptions import ImproperlyConfigured

# Database: Supabase Managed PostgreSQL in production, SQLite in local development
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and ('[YOUR-PASSWORD]' in DATABASE_URL or 'YOUR-PASSWORD' in DATABASE_URL or '[PASSWORD]' in DATABASE_URL):
    print("[Warning] DATABASE_URL contains placeholder password.")
    DATABASE_URL = None

if DATABASE_URL:
    is_postgres = DATABASE_URL.startswith(('postgres://', 'postgresql://'))
    parse_options = {
        'conn_max_age': 600,
        'conn_health_checks': True,
    }
    if is_postgres:
        parse_options['ssl_require'] = True

    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            **parse_options
        )
    }
elif DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    raise ImproperlyConfigured(
        "DATABASE CONFIGURATION ERROR: In production mode (DEBUG=False), the DATABASE_URL environment variable "
        "must be configured with a persistent database connection (e.g. Supabase Managed PostgreSQL). "
        "Running on ephemeral SQLite in production is strictly prohibited as user accounts and order records will be lost on container restart. "
        "Please configure DATABASE_URL in your Render Dashboard environment settings."
    )

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cloudinary Persistent Media Storage for Production
if USE_CLOUDINARY:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY': CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }

# Support up to 50MB file uploads for multi-image high-res product photos
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cashfree Payment Gateway Configuration
CASHFREE_CLIENT_ID = os.getenv('CASHFREE_CLIENT_ID', '').strip()
CASHFREE_CLIENT_SECRET = os.getenv('CASHFREE_CLIENT_SECRET', '').strip()
CASHFREE_ENVIRONMENT = os.getenv('CASHFREE_ENVIRONMENT', 'SANDBOX').strip().upper()
CASHFREE_API_VERSION = os.getenv('CASHFREE_API_VERSION', '2023-08-01').strip()
CASHFREE_BASE_URL = 'https://api.cashfree.com' if CASHFREE_ENVIRONMENT == 'PRODUCTION' else 'https://sandbox.cashfree.com'

