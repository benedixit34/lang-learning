import os
from distutils.util import strtobool

from .base import *  # noqa F401

DEBUG = os.getenv("DEBUG")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": 5432,
    }
}

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "standard": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
#     },
#     "handlers": {
#         "console": {
#             "level": "INFO",
#             "class": "logging.StreamHandler",
#             "formatter": "standard",
#             "filters": [],
#         },
#     },
#     "loggers": {
#         logger_name: {
#             "level": "WARNING",
#             "propagate": True,
#         }
#         for logger_name in (
#             "django",
#             "django.request",
#             "django.db.backends",
#             "django.template",
#             "cooking_core",
#         )
#     },
#     "root": {
#         "level": "DEBUG",
#         "handlers": ["console"],
#     },
# }

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST=os.getenv('EMAIL_HOST')
EMAIL_PORT=587
EMAIL_HOST_USER=os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD=os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS =True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=os.getenv('DEFAULT_FROM_ EMAIL')

# celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_BACKEND", "redis://redis:6379/0")
