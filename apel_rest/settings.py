"""
Django settings for apel_rest project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'Put a secret here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.RemoteUserBackend',
# )

ROOT_URLCONF = 'apel_rest.urls'

WSGI_APPLICATION = 'apel_rest.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = '/var/www/html/static'
STATIC_URL = '/accounting-server/static/'

# debugging stuff
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s]: %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s: %(message)s'
        },
    },
    'handlers': {
        # 'file': {
        #     'class': 'logging.FileHandler',
        #     'filename': './apel_rest.log',
        #     'formatter': 'verbose'
        # },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'api': {
            'handlers': ['console'],
            'level': 'INFO',
            #'level': 'DEBUG',
        },
    }
}

# XML stuff
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'apel_rest.PlainTextParser.PlainTextParser',
    ),
    # this would add HTML buttons for pagination, but only in 3.3
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework_xml.renderers.XMLRenderer',
    # ),
}

# Defines where the REST API will store
# incoming messages for later processing
QPATH = '/var/spool/apel/cloud'

# Defines the database settings
# used by the REST API
CLOUD_DB_CONF = '/etc/apel/clouddb.cfg'

# Defines the maximum results per page
# returned from the REST API
RESULTS_PER_PAGE = 100

# Defines what field to return
# in the REST API
RETURN_HEADERS = ["VOGroup",
                  "SiteName",
                  "UpdateTime",
                  "WallDuration",
                  "EarliestStartTime",
                  "LatestStartTime",
                  "Day",
                  "Month",
                  "Year"]

# this should hide the GET?format button
# this doesnt do anything, probably because of using older Django
URL_FORMAT_OVERRIDE = None
