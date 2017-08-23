# Renomear esse arquivo local_settings.py
# Apos renomeado, deve ser inserido no hgignore

DEBUG = True

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '<nome do banco de dados>',
        'USER': '<usuario do banco de dados>',
        'PASSWORD': '<senha do banco de dados>',
        'HOST': 'localhost ou 127.0.0.1',
        'PORT': '5432'
    }
}
