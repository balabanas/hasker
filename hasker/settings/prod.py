from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_vars['POSTGRES_DB'],
        'USER': env_vars['POSTGRES_USER'],
        'PASSWORD': env_vars['POSTGRES_PASSWORD'],
        'HOST': env_vars['POSTGRES_HOST'],
        'PORT': env_vars['POSTGRES_PORT'],
    }
}
