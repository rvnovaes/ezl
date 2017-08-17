#Renomear esse arquivo local_settings.py
#Apos renomeado, deve ser inserido no hgignore
import os

DEBUG = True

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '<servidor>',
        'USER': '<usuario servidor>',
        'PASSWORD': '<senha servidor>',
        'HOST': 'localhost',
        # 'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}
