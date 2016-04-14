import json
import os

from chiton.core.environment import use_config

with open(os.environ['CHITON_CONFIG_FILE']) as config_file:
    config = use_config(json.load(config_file))

CHITON_ROOT = os.path.dirname(os.path.abspath(__file__))

# Environment
# ==============================================================================

DEBUG = config['debug']
SECRET_KEY = config['secret_key']

# Locale
# ==============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Application
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'adminsortable2',
    'raven.contrib.django.raven_compat',

    'chiton.core.apps.Config',
    'chiton.closet.apps.Config',
    'chiton.rack.apps.Config',
    'chiton.runway.apps.Config'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': config['debug']
        },
    },
]

# Database
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % config['database']['engine'],
        'HOST': config['database'].get('host'),
        'NAME': config['database']['name'],
        'PASSWORD': config['database'].get('password'),
        'PORT': config['database'].get('port'),
        'USER': config['database'].get('user')
    }
}

# Email
# ==============================================================================

DEFAULT_FROM_EMAIL = config['default_email']
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
SERVER_EMAIL = config['server_email']

# Logging
# ==============================================================================

LOGGING = {
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': config['log_file']
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file' if config['file_logging'] else 'console'],
            'level': config['log_level'],
            'propagate': True
        }
    },
    'version': 1
}

if config['track_errors']:
    RAVEN_CONFIG = {
        'dsn': config['sentry_dsn'],
        'site': config['environment'].capitalize()
    }

# Assets
# ==============================================================================

STATIC_ROOT = config['static_root']
STATIC_URL = config['static_url']
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Serving
# ==============================================================================

ALLOWED_HOSTS = config['allowed_hosts']
APPEND_SLASH = True
CSRF_COOKIE_SECURE = True
ROOT_URLCONF = 'chiton.urls'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
WSGI_APPLICATION = 'chiton.wsgi.application'

# API Credentials
# ==============================================================================

AMAZON_ASSOCIATES_TRACKING_ID = config['amazon_associates_tracking_id']
AMAZON_ASSOCIATES_AWS_ACCESS_KEY_ID = config['amazon_associates_aws_access_key_id']
AMAZON_ASSOCIATES_AWS_SECRET_ACCESS_KEY = config['amazon_associates_aws_secret_access_key']

SHOPSTYLE_UID = config['shopstyle_uid']
