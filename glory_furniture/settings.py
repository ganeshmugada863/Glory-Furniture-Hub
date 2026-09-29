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
    'https://*.vercel.app',
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
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    *(['cloudinary_storage'] if USE_CLOUDINARY else []),
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
def sanitize_database_url(url: str) -> str:
    """Sanitize database URL to properly handle special characters in password,

    remove stray quotes, and convert IPv6 Supabase direct hosts to IPv4 connection pooler.
    """
    if not url:
        return url
    url = url.strip().strip("'\"")
    import re
    import urllib.parse
    m = re.match(
        r'^(?P<scheme>[a-zA-Z0-9+]+)://(?P<user>[^:]+):(?P<password>.+)@(?P<host>[^:/]+)(?::(?P<port>\d+))?(?P<path>/[^?#]*)?(?P<query>\?.*)?$',
        url
    )
    if not m:
        return url
    d = m.groupdict()
    scheme = d['scheme']
    user = d['user']
    raw_pw = d['password'].strip().strip("'\"")
    if raw_pw.startswith('[') and raw_pw.endswith(']'):
        raw_pw = raw_pw[1:-1].strip()
    pw = urllib.parse.quote_plus(urllib.parse.unquote(raw_pw))
    host = d['host']
    port = d['port'] or '5432'
    path = d['path'] or '/postgres'
    query = d['query'] or ''

    # Supabase direct host (db.<ref>.supabase.co) resolves to IPv6 only,
    # which fails on AWS Lambda / Vercel with "Cannot assign requested address".
    # Automatically rewrite to Supabase's IPv4 connection pooler (Supavisor).
    m_sb = re.match(r'^db\.([a-z0-9]+)\.supabase\.co$', host)
    if m_sb:
        ref = m_sb.group(1)
        if not user.endswith('.' + ref):
            user = f"{user}.{ref}"
        region = os.getenv('SUPABASE_REGION', 'ap-southeast-1')
        host = f"aws-0-{region}.pooler.supabase.com"
        port = os.getenv('SUPABASE_POOLER_PORT', '5432')

    if 'aws-0-ap-south-1.pooler.supabase.com' in host:
        host = 'aws-0-ap-southeast-1.pooler.supabase.com'

    if 'pooler.supabase.com' in host and not ('.' in user):
        user = f"{user}.qxxrghelhlrafdkveeqo"

    print(f"[DB Init] Host={host}, Port={port}, User={user}, PW_len={len(raw_pw)}")

    return f"{scheme}://{user}:{pw}@{host}:{port}{path}{query}"

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASE_URL = sanitize_database_url(DATABASE_URL)
    if any(placeholder in DATABASE_URL for placeholder in ('[YOUR-PASSWORD]', 'YOUR-PASSWORD', '[PASSWORD]')):
        print("[Warning] DATABASE_URL contains placeholder password.")
        DATABASE_URL = None

if DATABASE_URL:
    try:
        is_postgres = DATABASE_URL.startswith(('postgres://', 'postgresql://'))
        conn_max = 0 if os.getenv('VERCEL') else 600
        parse_options = {
            'conn_max_age': conn_max,
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
    except Exception as e:
        print(f"[Warning] Failed to parse DATABASE_URL: {e}. Falling back to SQLite.")
        if DEBUG or os.getenv('VERCEL'):
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / 'db.sqlite3',
                }
            }
        else:
            raise
elif DEBUG or os.getenv('VERCEL'):
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
        "Please configure DATABASE_URL in your deployment environment settings."
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
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

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

