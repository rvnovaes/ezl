
import os
import sys
from config.config import get_parser


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_MANUAL_URL = '/static/downloads/manual-correspondentes.pdf'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
parser = get_parser()
try:
    source = dict(parser.items('django_application'))
    source_etl = dict(parser.items('etl'))
    engine = source['engine']
    database = source['database']
    user = source['user']
    password = source['password']
    host = source['host']
    port = source['port']
    environment = source['environment']
    email_use_ssl = source['email_use_ssl']
    email_host = source['email_host']
    email_port = source['email_port']
    email_host_user = source['email_host_user']
    email_host_password = source['email_host_password']
    linux_password = source_etl['linux_password']
    linux_user = source_etl['linux_user']
    if not os.path.exists('/var/log/ezl/etl'):
        os.system('echo {0}|sudo -S mkdir -p /var/log/ezl/etl/'.format(
            linux_password))
        os.system('echo {0}|sudo -S chmod 755 /var/log/ezl/etl/ -R'.format(
            linux_password))
        os.system('echo {0}|sudo -S chown -R {1} /var/log/ezl/etl/'.format(
            linux_password, linux_user))
        os.system('echo {0}|sudo -S chown -R {1} /var/log/ezl/'.format(
            linux_password, linux_user))

except KeyError as e:
    print('Invalid settings. Check the General.ini file')
    print(e)
    sys.exit(0)

from django.urls import reverse_lazy
import datetime


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f5*(8sgk)n1!i52xijv0yt@jtewp28%g%sp1rx*=y68ocgg+!2'

# SECURITY WARNING: don't run with debug turned on in production!
if environment == 'development':
    DEBUG = True
else:
    DEBUG = False

DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'material.theme.teal',
    'material',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'core.apps.CoreConfig',
    'lawsuit.apps.LawsuitConfig',
    'task.apps.TaskConfig',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'django_tables2',
    'bootstrap3',
    'django_filters',
    'debug_toolbar',
    'django_cleanup',
    # Autocomplete
    'dal',
    # Enable plugins
    'dal_select2',
    'dal_queryset_sequence',
    # Test
    'localflavor',
    #Sequences
    'sequences.apps.SequencesConfig'
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'ezl.urls'
SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'core/templates'),
                 os.path.join(BASE_DIR, 'core/templates/core/http_errors')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media'
            ],
        },
    },
]

WSGI_APPLICATION = 'ezl.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': engine,
        'NAME': database,
        'USER': user,
        'PASSWORD': password,
        'HOST': host,
        'PORT': port
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
if environment == 'development':
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': 1,
            }
        },
    ]
else:
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
# STATIC_ROOT = ''

STATIC_URL = '/static/'

#TODO Mover a pasta static/static para a app static/static
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Pasta para qual os arquivos estaticos sao copiados com manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = '/opt/files_easy_lawyer/'

LOGIN_REDIRECT_URL = reverse_lazy('dashboard')

AUTHENTICATION_BACKENDS = (

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Host configuration to send email
EMAIL_USE_SSL = email_use_ssl
EMAIL_HOST = email_host
EMAIL_PORT = email_port
EMAIL_HOST_USER = email_host_user
EMAIL_HOST_PASSWORD = email_host_password


INTERNAL_IPS = '127.0.0.1'
PROJECT_NAME = 'Easy Lawyer'
PROJECT_LINK = 'https://ezl.mtostes.com.br'

LINK_TO_RESTORE_DB_DEMO = 'http://13.68.213.60:8001'

RAVEN_CONFIG = {
    'dsn': 'https://8117af934e9c436c8ad81a66fd875912:d00c54e22db046b19a7dcae5677126db@sentry.io/224925',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'development_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': '/tmp/django_dev.log',
            'formatter': 'verbose'
        },
        'ezl_logfile': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': '/var/log/ezl/ezl.log',
            'formatter': 'simple'
        },
        'error_logfile': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': '/var/log/ezl/etl/'+datetime.datetime.now().strftime("error_%Y%m%d_%H%M%S.log"),
            'formatter': 'simple'
        },
        'debug_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': '/var/log/ezl/etl/'+datetime.datetime.now().strftime("debug_%Y%m%d_%H%M%S.log"),
            'formatter': 'simple'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'loggers': {
        'coffeehouse': {
            'handlers': ['development_logfile'],
         },
        'error_logger': {
            'handlers': ['error_logfile'],
            'level': 'ERROR'
        },
        'debug_logger': {
            'handlers': ['debug_logfile'],
            'level': 'DEBUG'
        },
        'ezl': {
            'handlers': ['ezl_logfile'],
            'level': 'INFO'
        },
        'django': {
            'handlers': ['development_logfile'],
        },
        'py.warnings': {
            'handlers': ['development_logfile'],
        },
    }
}
