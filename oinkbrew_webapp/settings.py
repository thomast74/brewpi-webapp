import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = '!f+8y8k8$djmc6!o9-h=^7=%uqyltzh!3@4iy)eq2h!y8nh@l='

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []
ROOT_URLCONF = 'oinkbrew_webapp.urls'
WSGI_APPLICATION = 'oinkbrew_webapp.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api'
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.oinkbrew '),
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'api-file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/oinkbrew/oinkbrew-api.log',
            'formatter': 'verbose'
        },
        'application-file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/oinkbrew/oinkbrew-application.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['application-file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'api': {
            'handlers': ['api-file'],
            'level': 'DEBUG',
        },
    }
}
