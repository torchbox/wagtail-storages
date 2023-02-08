import os

import django.utils.crypto

TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = django.utils.crypto.get_random_string(50)

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "wagtail.admin",
    "wagtail.documents",
    "wagtail.users",
    "wagtail",
    "wagtail.contrib.frontend_cache",
    "wagtail_storages.apps.WagtailStoragesConfig",
    "storages",
    "taggit",
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
            ],
        },
    },
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}}

# Some tests use the default the FileSystemStorage backend.
MEDIA_ROOT = os.path.join(TESTS_PATH, "media")

STATIC_ROOT = os.path.join(TESTS_PATH, "static")

ROOT_URLCONF = "wagtail_storages.tests.urls"

AWS_DEFAULT_ACL = "private"

# Disable querystring auth by default. Otherwise public files will be served
# with the auth.
AWS_QUERYSTRING_AUTH = False

# Do not override file names
AWS_S3_FILE_OVERWRITE = False

AWS_S3_CUSTOM_DOMAIN = "media.torchbox.com"

AWS_STORAGE_BUCKET_NAME = "test"

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
]

WAGTAILADMIN_BASE_URL = "http://example.com"
