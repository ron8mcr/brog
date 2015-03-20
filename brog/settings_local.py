DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'brogdb',
        'USER': 'broguser',
        'PASSWORD': 'brogpass',
        'HOST': '',  # Set to empty string for localhost.
        'PORT': '',  # Set to empty string for default.
    }
}

MEDIA_ROOT = '/home/roman/prog/python/django/brog/media'
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'
STATICFILES_DIRS = (
    'brog/static/',
)

SENDFILE_BACKEND = 'sendfile.backends.development'
# SENDFILE_BACKEND = 'sendfile.backends.nginx'
