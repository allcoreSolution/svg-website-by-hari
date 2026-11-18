import os
import sys
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Add apps directory to Python path
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

env = environ.Env(
    DEBUG=(bool, False),
    SITE_URL=(str, 'http://127.0.0.1:8000'),
)

env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file, overwrite=False)

DEBUG = env.bool('DEBUG', default=False)

if DEBUG:
    SECRET_KEY = env('SECRET_KEY', default='django-insecure-skyvision-dev-key-for-local-testing-only-replace-in-prod')
else:
    secret_key_val = env('SECRET_KEY', default='')
    if not secret_key_val or secret_key_val.startswith('django-insecure-'):
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            "SECRET_KEY must be set to a secure, non-default value in environment variables when DEBUG=False."
        )
    SECRET_KEY = secret_key_val

# ALLOWED_HOSTS read from environment with safe local fallback
raw_allowed_hosts = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost', 'testserver'])
if 'testserver' not in raw_allowed_hosts:
    raw_allowed_hosts.append('testserver')

# Render.com automatic hostname detection
render_host = env('RENDER_EXTERNAL_HOSTNAME', default=None)
if render_host and render_host not in raw_allowed_hosts:
    raw_allowed_hosts.append(render_host)
    raw_allowed_hosts.append(f'.onrender.com')

ALLOWED_HOSTS = raw_allowed_hosts

SITE_URL = env('SITE_URL', default=f'https://{render_host}' if render_host else 'http://127.0.0.1:8000')

# CSRF Trusted Origins
raw_csrf = env.list('CSRF_TRUSTED_ORIGINS', default=[])
if render_host:
    https_url = f'https://{render_host}'
    if https_url not in raw_csrf:
        raw_csrf.append(https_url)
    if 'https://*.onrender.com' not in raw_csrf:
        raw_csrf.append('https://*.onrender.com')

CSRF_TRUSTED_ORIGINS = raw_csrf

# CORS Allowed Origins
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://localhost:3000',
])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Sky Vision Custom Apps
    'apps.core.apps.CoreConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.candidates.apps.CandidatesConfig',
    'apps.companies.apps.CompaniesConfig',
    'apps.internships.apps.InternshipsConfig',
    'apps.placements.apps.PlacementsConfig',
    'apps.enquiries.apps.EnquiriesConfig',
    'apps.jobs.apps.JobsConfig',
    'apps.dashboard.apps.DashboardConfig',
    'apps.candidate_portal.apps.CandidatePortalConfig',
    'apps.employer_portal.apps.EmployerPortalConfig',
    'apps.ledger.apps.LedgerConfig',
    'apps.communication.apps.CommunicationConfig',
]

MIDDLEWARE = [
    'apps.core.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.accounts.middleware.AdminPermissionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'apps.dashboard.context_processors.admin_counts_context',
                'apps.core.context_processors.site_settings_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Supports DATABASE_URL (e.g. Render PostgreSQL) with automatic local SQLite fallback
database_url = env('DATABASE_URL', default=None)
if database_url:
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(
                default=database_url,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    except ImportError:
        if database_url.startswith('sqlite:////'):
            db_path = database_url.replace('sqlite:////', '/')
            import tempfile
            if not os.path.exists(os.path.dirname(db_path)) and os.name == 'nt':
                db_path = os.path.join(tempfile.gettempdir(), os.path.basename(db_path))
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': db_path,
                }
            }
        elif database_url.startswith('sqlite:///'):
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': database_url.replace('sqlite:///', ''),
                }
            }
        else:
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': os.path.join(BASE_DIR, 'database', 'database.db'),
                }
            }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'database', 'database.db'),
        }
    }

# Ensure directory exists for SQLite database
if DATABASES.get('default', {}).get('ENGINE') == 'django.db.backends.sqlite3':
    db_file_path = DATABASES['default'].get('NAME')
    if db_file_path and isinstance(db_file_path, (str, Path)):
        db_folder = os.path.dirname(os.path.abspath(str(db_file_path)))
        if db_folder and not os.path.exists(db_folder):
            os.makedirs(db_folder, exist_ok=True)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static & Media Configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise static files serving for Render / Production
try:
    import whitenoise
    if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
        sec_idx = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
        MIDDLEWARE.insert(sec_idx + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }
except ImportError:
    pass

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session configuration
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 8 * 60 * 60  # 8 hours

# Upload restrictions
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Email & Communication configuration
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

_default_from_addr = EMAIL_HOST_USER or 'info@skyvisiongroup.in'
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=f"Sky Vision Group <{_default_from_addr}>")

# Console backend fallback if credentials are missing
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_TIMEOUT = env.int('EMAIL_TIMEOUT', default=20)

# Communication Limits & Features
COMM_EMAIL_DAILY_LIMIT = env.int('COMM_EMAIL_DAILY_LIMIT', default=400)
COMM_EMAIL_BATCH_SIZE = env.int('COMM_EMAIL_BATCH_SIZE', default=20)
COMM_EMAIL_DELAY_SECONDS = env.float('COMM_EMAIL_DELAY_SECONDS', default=1.0)
COMM_REPLY_TO = env('COMM_REPLY_TO', default='')
COMM_ENABLE_SMS_WHATSAPP = env.bool('COMM_ENABLE_SMS_WHATSAPP', default=False)
COMM_STALE_SENDING_MINUTES = env.int('COMM_STALE_SENDING_MINUTES', default=10)
COMM_MAX_ATTACHMENT_MB = env.int('COMM_MAX_ATTACHMENT_MB', default=5)

# Production security settings (activated when DEBUG=False)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
    SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=3600)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
    SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)
# Ledger & Commission settings
LEDGER_COMMISSION_PERCENT = env.float('LEDGER_COMMISSION_PERCENT', default=50.0)
LEDGER_DEFAULT_DUE_DAYS = env.int('LEDGER_DEFAULT_DUE_DAYS', default=30)

