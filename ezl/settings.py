import datetime
import os
import sys
import tempfile

# Todas as variáveis de configuração devem ser criadas nos arquivos desta pasta
from config.config import get_parser

from django.urls import reverse_lazy
from decimal import ROUND_HALF_EVEN
import moneyed
from moneyed.localization import _FORMATTER, DEFAULT
from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

parser = get_parser()
try:
    source = dict(parser.items('django_application'))
    source_etl = dict(parser.items('etl'))
    source_redis = dict(parser.items('redis'))
    engine = source['engine']
    database = source['database']
    user = source['user']
    password = source['password']
    host = os.environ.get('DB_HOST', source['host'])
    port = os.environ.get('DB_PORT', source['port'])
    environment = source['environment']
    email_use_ssl = True if os.environ.get(
        'EMAIL_USE_SSL', source['email_use_ssl'].lower()) == "true" else False
    email_host = os.environ.get('EMAIL_HOST', source['email_host'])
    email_port = os.environ.get('EMAIL_PORT', source['email_port'])
    email_host_user = source['email_host_user']
    email_host_password = source['email_host_password']
    email_default_from_email = source['email_default_from_email']
    email_default_to_email = source.get('email_default_to_email', None)
    linux_password = source_etl['linux_password']
    linux_user = source_etl['linux_user']

    redis_host = source_redis['host']
    redis_port = source_redis['port']


except KeyError as e:
    print('Invalid settings. Check the General.ini file')
    print(e)
    sys.exit(0)



MUST_LOGIN = True

CELERY_BROKER_URL = 'amqp://guest:guest@queues:5672/'
CELERY_RESULT_BACKEND = 'amqp://guest:guest@queues:5672/'
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BEAT_SCHEDULE = {
    'task-remove_old_etldashboard': {
        'task': 'etl.tasks.remove_old_etldashboard',
        'schedule': crontab(minute=0, hour=2)
    },
    'task-clear_sessions': {
        'task': 'core.tasks.clear_sessions',
        'schedule': crontab(minute=0, hour=3)
    },
}
CELERY_SEND_TASK_EMAILS = False
CELERY_TASK_IGNORE_RESULT = True


DATETIME_FORMAT = '%d/%m/%Y %H:%M'



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f5*(8sgk)n1!i52xijv0yt@jtewp28%g%sp1rx*=y68ocgg+!2'

# SECURITY WARNING: don't run with debug turned on in production!

WORKFLOW_URL_EMAIL = os.environ.get('WORKFLOW_EMAIL', 'http://localhost:8000')

if environment in ['debug', 'development']:
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
CSRF_TRUSTED_ORIGINS = ['.ezlawyer.com.br']

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
    'advwin_models',
    'core.apps.CoreConfig',
    'lawsuit.apps.LawsuitConfig',
    'task.apps.TaskConfig',
    'etl.apps.EtlConfig',
    'financial.apps.FinancialConfig',
    'survey.apps.SurveyConfig',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.openid',
    'celery',
    'django_tables2',
    'django_filters',
    'bootstrap3',
    'django_file_form',
    'django_file_form.ajaxuploader',
    'debug_toolbar',
    'django_extensions',
    'django_cleanup',
    # Autocomplete
    'dal',
    # Enable plugins
    'dal_select2',
    'dal_queryset_sequence',
    # Test
    'localflavor',
    # Sequences
    'sequences.apps.SequencesConfig',
    'channels',
    'chat.apps.ChatConfig',
    'ecm',
    'dashboard',
    'codemirror',
    'guardian',
    'billing',
    'djmoney',
    'rest_framework',
    'rest_framework_swagger',
    'oauth2_provider',
    'import_export',
    'django_dbconn_retry',
    'rest_auth',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ezl.urls'
SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND':
        'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'core/templates'),
            os.path.join(BASE_DIR, 'core/templates/core/http_errors'),
            os.path.join(BASE_DIR, 'ecm/templates')
        ],
        'APP_DIRS':
        True,
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

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            'hosts': [(redis_host, int(redis_port))],
        },
        "ROUTING": "chat.routing.channel_routing"
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://{redis_host}:{redis_port}/1'.format(redis_host=redis_host, redis_port=redis_port),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
if environment in ['debug', 'development']:
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': 1,
            }
        },
    ]
else:
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# configuração de formatação de moeda para o campo de Money da biblioteca django-money
_FORMATTER.add_sign_definition('pt_BR', moneyed.BRL, prefix='R$')
_FORMATTER.add_sign_definition(DEFAULT, moneyed.BRL, prefix='R$')
_FORMATTER.add_formatting_definition(
    'pt_BR',
    group_size=3,
    group_separator='.',
    decimal_point=',',
    positive_sign='',
    trailing_positive_sign='',
    negative_sign='-',
    trailing_negative_sign='',
    rounding_method=ROUND_HALF_EVEN)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
# STATIC_ROOT = ''

STATIC_URL = '/static/'

# TODO Mover a pasta static/static para a app static/static
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )

# Pasta para qual os arquivos estaticos sao copiados com manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAJTB675KE6AXUTPKA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False
if environment == 'production':
    AWS_STORAGE_BUCKET_NAME = 'ezl-production'
else:
    AWS_STORAGE_BUCKET_NAME = 'ezl-development'
AWS_STORAGE_BUCKET_URL = 'https://{}.s3.amazonaws.com/'.format(
    AWS_STORAGE_BUCKET_NAME)

LOGIN_REDIRECT_URL = reverse_lazy('inicial')

AUTHENTICATION_BACKENDS = (

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
)

# Host configuration to send email

EMAIL_USE_SSL = email_use_ssl
EMAIL_HOST = email_host
EMAIL_PORT = email_port
EMAIL_HOST_USER = email_host_user
EMAIL_HOST_PASSWORD = email_host_password
DEFAULT_FROM_EMAIL = email_default_from_email
DEFAULT_TO_EMAIL = email_default_to_email

INTERNAL_IPS = '127.0.0.1'
PROJECT_NAME = 'Easy Lawyer'
PROJECT_LINK = 'https://ezl.ezlawyer.com.br'

LUIGI_TARGET_PATH = os.path.join(BASE_DIR, 'luigi_targets')

if os.name == 'nt':
    LOG_DIR = os.path.join(tempfile.gettempdir(), 'ezl')
else:
    LOG_DIR = '/var/log/ezl'

LOG_FILE_TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

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
            'format':
            '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt':
            '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        # 'mail_admins': {
        #     'level': 'ERROR',
        #     'class': 'django.utils.log.AdminEmailHandler',
        #     'include_html': True,
        #     'filters': ['require_debug_false'],
        # },
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
            'filename': os.path.join(LOG_DIR, 'django_dev.log'),
            'formatter': 'verbose'
        },
        'ezl_logfile': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'ezl.log'),
            'formatter': 'simple'
        },
        'error_logfile': {
            'level':
            'ERROR',
            'class':
            'logging.FileHandler',
            'filename':
            os.path.join(LOG_DIR,
                         'etl/error_{}.log'.format(LOG_FILE_TIMESTAMP)),
            'formatter':
            'simple'
        },
        'debug_logfile': {
            'level':
            'DEBUG',
            'class':
            'logging.FileHandler',
            'filename':
            os.path.join(LOG_DIR,
                         'etl/debug_{}.log'.format(LOG_FILE_TIMESTAMP)),
            'formatter':
            'simple'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'loggers': {
        'advwin_models.tasks': {
            'handlers': [
                'console',
                'error_logfile',
                'ezl_logfile',
                'debug_logfile',
                'development_logfile',
            ],
        },
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
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
    }
}

UPLOAD_DIRECTORY = 'uploads'
# ADMINS = [('EZL Erros', 'erros.ezlawyer@gmail.com')]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':
    ('oauth2_provider.contrib.rest_framework.OAuth2Authentication', ),
    'DEFAULT_FILTER_BACKENDS':
    ('django_filters.rest_framework.DjangoFilterBackend', ),
    'DEFAULT_PAGINATION_CLASS':
    'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE':
    30,
}

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore',
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'groups': 'Access to your groups'
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': 36000,
}

OAUTH2_PROVIDER_APPLICATION_MODEL = 'core.ExternalApplication'

SWAGGER_SETTINGS = {
    'LOGIN_URL': 'rest_framework:login',
    'LOGOUT_URL': 'rest_framework:logout',
    'USE_SESSION_AUTH': True,
    'DOC_EXPANSION': 'list',
    'APIS_SORTER': 'alpha',
    'SECURITY_DEFINITIONS': None,
    'JSON_EDITOR': True,
    'OPERATIONS_SORTER': 'method',
    'SHOW_REQUEST_HEADERS': True,
}

# configuração para o django_import_export
DATETIME_INPUT_FORMATS = (
    '%d/%m/%Y %H:%M',
    '%d/%m/%Y %H:%M',
)

SOCIALACCOUNT_ADAPTER = 'core.account.adapter.EzlSocialAccountAdapter'
ACCOUNT_AUTHENTICATION_METHOD = "username"
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
