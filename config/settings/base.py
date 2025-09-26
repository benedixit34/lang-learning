import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True


ALLOWED_HOSTS = [
    "*",
    "16.170.120.178",
    "api.learn.afroeuropean.uk",
    "learn.afroeuropean.uk",
    "staging.learn.afroeuropean.uk",
    "localhost",
    "127.0.0.1",
]

CORS_ORIGIN_ALLOW_ALL = True


CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "Stripe-Signature",
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


CORS_ALLOWED_ORIGINS = [
    "https://learn.afroeuropean.uk",
    "https://staging.learn.afroeuropean.uk",
    "https://api.learn.afroeuropean.uk",
    "http://localhost",
    "http://127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://learn.afroeuropean.uk",
    "https://api.learn.afroeuropean.uk",
    "https://staging.learn.afroeuropean.uk",
]

CORS_EXPOSE_HEADERS = ["Set-Cookie"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party apps
    "cloudinary",
    "cloudinary_storage",
    "django_extensions",
    "drf_spectacular",
    "rest_framework",
    "rest_framework_simplejwt",
    "whitenoise",
    "corsheaders",
    "drf_stripe",
    "django_crontab",
    # local apps
    "app.accounts",
    "app.auth",
    "app.courses",
    "app.support",
]

DRF_STRIPE = {
    "STRIPE_API_SECRET": os.getenv("STRIPE_API_SECRET"),
    "STRIPE_WEBHOOK_SECRET": os.getenv("STRIPE_WEBHOOK_SECRET"),
    "FRONT_END_BASE_URL": os.getenv("FRONTEND_BASE_URL"),
    "CHECKOUT_SUCCESS_URL_PATH": os.getenv("CHECKOUT_SUCCESS_URL_PATH"),
    "CHECKOUT_CANCEL_URL_PATH": os.getenv("CHECKOUT_CANCEL_URL_PATH"),
    "DJANGO_USER_EMAIL_FIELD": "email",
    "DJANGO_USER_MODEL": "accounts.CustomUser",
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

CRONJOBS = [
    ('* * * * *', 'drf_stripe.management.commands.pull_stripe'),
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

SESSON_COOKIE_DOMAIN = None

WSGI_APPLICATION = "config.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "app.accounts.backends.EmailBackend",
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "contents/"
MEDIA_ROOT = BASE_DIR / "static/contents"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.CustomUser"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUD_NAME"),
    "API_KEY": os.getenv("API_KEY"),
    "API_SECRET": os.getenv("API_SECRET"),
    "SECURE": True,
    "MEDIA_TAG": "media",
    "INVALID_VIDEO_ERROR_MESSAGE": "Please upload a valid video file.",
    "EXCLUDE_DELETE_ORPHANED_MEDIA_PATHS": (),
    "STATIC_TAG": "static",
    "STATICFILES_MANIFEST_ROOT": os.path.join(BASE_DIR, "manifest"),
    "STATIC_IMAGES_EXTENSIONS": [
        "jpg",
        "jpe",
        "jpeg",
        "jpc",
        "jp2",
        "j2k",
        "wdp",
        "jxr",
        "hdp",
        "png",
        "gif",
        "webp",
        "bmp",
        "tif",
        "tiff",
        "ico",
    ],
    "STATIC_VIDEOS_EXTENSIONS": [
        "mp4",
        "webm",
        "flv",
        "mov",
        "ogv",
        "3gp",
        "3g2",
        "wmv",
        "mpeg",
        "flv",
        "mkv",
        "avi",
    ],
    "MAGIC_FILE_PATH": "magic",
}

MEDIA_URL = "/media/"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "USER_ID_FIELD": "email",
    "SIGNING_KEY": os.getenv("SIGNING_KEY"),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "AE Learning API",
    "DESCRIPTION": "Backend API for AE Learning",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v1/",
}
