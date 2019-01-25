import datetime
import os
import sys
import tempfile

# Todas as variáveis de configuração devem ser criadas nos arquivos da pasta ezl/config
from config.config import get_parser

from django.urls import reverse_lazy
from decimal import ROUND_HALF_EVEN
import moneyed
from moneyed.localization import _FORMATTER, DEFAULT
from celery.schedules import crontab

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = get_parser()
try:
    engine = config['django_application']['engine']
    database = config['django_application']['database']
    user = config['django_application']['user']
    password = config['django_application']['password']
    host = config['django_application']['host']
    port = config['django_application']['port']
    environment = config['django_application']['environment']
    email_use_ssl = config['django_application'].getboolean('email_use_ssl')
    email_host = config['django_application']['email_host']
    email_port = config['django_application']['email_port']
    email_host_user = config['django_application']['email_host_user']
    email_host_password = config['django_application']['email_host_password']
    email_default_from_email = config['django_application']['email_default_from_email']
    email_default_to_email = config['django_application']['email_default_to_email']
    language_code = config['django_application']['language_code']
    timezone = config['django_application']['timezone']
    use_i18n = config['django_application'].getboolean('use_i18n')
    use_l10n = config['django_application'].getboolean('use_l10n')
    use_tz = config['django_application'].getboolean('use_tz')
    datetime_format = config['django_application']['datetime_format']
    log_date_format = config['django_application']['log_date_format']
    secret_key = config['django_application']['secret_key']
    internal_ips = config['django_application']['internal_ips']
    project_name = config['django_application']['project_name']
    project_link = config['django_application']['project_link']

    linux_password = config['etl']['linux_password']
    linux_user = config['etl']['linux_user']

    redis_host = config['redis']['host']
    redis_port = config['redis']['port']

    celery_host = config['celery']['host']
    celery_port = config['celery']['port']
    celery_user = config['celery']['user']
    celery_password = config['celery']['password']
    celery_enable_utc = config['celery'].getboolean('enable_utc')
    celery_task_always_eager = config['celery'].getboolean('task_always_eager')
    celery_beat_schedule_dashboard = int(config['celery']['beat_schedule_dashboard'])
    celery_beat_schedule_clear_sessions = int(config['celery']['beat_schedule_clear_sessions'])
    celery_send_task_emails = config['celery'].getboolean('send_task_emails')
    celery_task_ignore_result = config['celery'].getboolean('task_ignore_result')

    default_file_storage = config['aws']['default_file_storage']
    aws_access_key_id = config['aws']['aws_access_key_id']
    aws_secret_access_key = config['aws']['aws_secret_access_key']
    aws_querystring_auth = config['aws'].getboolean('aws_querystring_auth')
    aws_s3_file_overwrite = config['aws'].getboolean('aws_s3_file_overwrite')
    aws_storage_bucket_url = config['aws']['aws_storage_bucket_url']

    rest_page_size = config['rest_framework']['page_size']
    rest_access_token_expire = config['rest_framework']['access_token_expire']

    socialaccount_adapter = config['social_auth']['socialaccount_adapter']
    account_authentication_method = config['social_auth']['account_authentication_method']
    socialaccount_query_email = config['social_auth'].getboolean('socialaccount_query_email')
    account_email_required = config['social_auth'].getboolean('account_email_required')

except KeyError as e:
    print('Invalid settings. Check ini files on ezl/config')
    print(e)
    sys.exit(0)

MUST_LOGIN = True
DATETIME_FORMAT = datetime_format

CELERY_BROKER_URL = 'amqp://{user}:{password}@{host}:{port}/'.format(user=celery_user,
                                                                     password=celery_password,
                                                                     host=celery_host,
                                                                     port=celery_port)
CELERY_RESULT_BACKEND = 'amqp://{user}:{password}@{host}:{port}/'.format(user=celery_user,
                                                                         password=celery_password,
                                                                         host=celery_host,
                                                                         port=celery_port)
CELERY_ENABLE_UTC = celery_enable_utc
CELERY_TIMEZONE = timezone
CELERY_TASK_ALWAYS_EAGER = celery_task_always_eager
CELERY_BEAT_SCHEDULE = {
    'task-remove_old_etldashboard': {
        'task': 'etl.tasks.remove_old_etldashboard',
        'schedule': crontab(minute=0, hour=celery_beat_schedule_dashboard)
    },
    'task-clear_sessions': {
        'task': 'core.tasks.clear_sessions',
        'schedule': crontab(minute=0, hour=celery_beat_schedule_clear_sessions)
    },
}
CELERY_SEND_TASK_EMAILS = celery_send_task_emails
CELERY_TASK_IGNORE_RESULT = celery_task_ignore_result

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret_key

WORKFLOW_URL_EMAIL = os.environ.get('WORKFLOW_EMAIL', 'http://localhost:8000')

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
CSRF_TRUSTED_ORIGINS = ['.ezlawyer.com.br']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    # Project apps
    'advwin_models',
    'billing.apps.BillingConfig',
    'chat.apps.ChatConfig',
    'core.apps.CoreConfig',
    'dashboard.apps.DashboardConfig',
    'ecm.apps.EcmConfig',
    'etl.apps.EtlConfig',
    'financial.apps.FinancialConfig',
    'lawsuit.apps.LawsuitConfig',
    'survey.apps.SurveyConfig',
    'task.apps.TaskConfig',

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
    'django_extensions',
    'django_cleanup',
    # Autocomplete
    'dal',
    # Enable plugins
    'dal_select2',
    'dal_queryset_sequence',
    # Test
    'localflavor',
    # TODO: Verificar necessidade de manter o material, com a troca do tema para o Ample
    'material',
    'material.theme.teal',
    # Sequences
    'sequences.apps.SequencesConfig',
    'channels',
    'codemirror',
    'guardian',
    'djmoney',
    'rest_framework',
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
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'core/templates'),
            os.path.join(BASE_DIR, 'core/templates/core/http_errors'),
            os.path.join(BASE_DIR, 'ecm/templates')
        ],
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
# SECURITY WARNING: don't run with debug turned on in production!
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
    DEBUG = True
    INSTALLED_APPS.append('debug_toolbar')
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
    DEBUG = False
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

LANGUAGE_CODE = language_code
TIME_ZONE = timezone
USE_I18N = use_i18n
USE_L10N = use_l10n
USE_TZ = use_tz

# configuração de formatação de moeda para o campo de Money da biblioteca django-money
_FORMATTER.add_sign_definition(language_code, moneyed.BRL, prefix='R$')
_FORMATTER.add_sign_definition(DEFAULT, moneyed.BRL, prefix='R$')
_FORMATTER.add_formatting_definition(
    language_code,
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

DEFAULT_FILE_STORAGE = default_file_storage
AWS_ACCESS_KEY_ID = aws_access_key_id
AWS_SECRET_ACCESS_KEY = aws_secret_access_key
AWS_QUERYSTRING_AUTH = aws_querystring_auth
AWS_S3_FILE_OVERWRITE = aws_s3_file_overwrite
AWS_STORAGE_BUCKET_URL = aws_storage_bucket_url

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

INTERNAL_IPS = internal_ips
PROJECT_NAME = project_name
PROJECT_LINK = project_link

LUIGI_TARGET_PATH = os.path.join(BASE_DIR, 'luigi_targets')

if os.name == 'nt':
    LOG_DIR = os.path.join(tempfile.gettempdir(), 'ezl')
else:
    LOG_DIR = '/var/log/ezl'

LOG_FILE_TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_DATE_FORMAT = log_date_format

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
            'datefmt': LOG_DATE_FORMAT
        },
        'verbose': {
            'format':
            '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': LOG_DATE_FORMAT
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

# Configurações para a API
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('oauth2_provider.contrib.rest_framework.OAuth2Authentication', ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend', ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(rest_page_size),
}

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore',
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'groups': 'Access to your groups'
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': int(rest_access_token_expire),
}

OAUTH2_PROVIDER_APPLICATION_MODEL = 'core.ExternalApplication'

# configuração para o django_import_export
DATETIME_INPUT_FORMATS = (
    datetime_format,
    datetime_format,
)

# configurações de autenticação via google API
SOCIALACCOUNT_ADAPTER = socialaccount_adapter
ACCOUNT_AUTHENTICATION_METHOD = account_authentication_method
SOCIALACCOUNT_QUERY_EMAIL = socialaccount_query_email
ACCOUNT_EMAIL_REQUIRED = account_email_required




""" 
Todo, levar estas configuracoes para os arquivos .conf organizados pelo Roberto 
na tarefa EZL-1198. 
"""
if environment == 'development':
    GERENCIANET_CREDENTIALS = {
        'client_id': 'Client_Id_f6db389974a3fc3b378efc90fffb67b154ae26ca', 
        'client_secret': 'Client_Secret_d408879045f6f877a44cd62e542eef24f0f387ce', 
        'sandbox': True
    }
else:
    GERENCIANET_CREDENTIALS = {
        'client_id': 'Client_Id_de299c3f0fe9c4bd607871a714665db65b54b23b', 
        'client_secret': 'Client_Secret_44cdc45c058e90bc1783d73f18e27ba47732f22d', 
        'sandbox': False
    }    