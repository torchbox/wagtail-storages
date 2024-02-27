import os

import django.utils.crypto

from wagtail import VERSION as WAGTAIL_VERSION

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

if WAGTAIL_VERSION >= (5, 2):
    # when running tests with Wagtail 5.2+, we need to set the STATIC_URL explicitly,
    # otherwise the test server will not start.
    # This happens when running tests against the main branch of Wagtail
    # so I am assuming that an upcoming release will require this.
    STATIC_URL = "/static/"

ROOT_URLCONF = "wagtail_storages.tests.urls"

AWS_DEFAULT_ACL = "private"

# Disable querystring auth by default. Otherwise public files will be served
# with the auth.
AWS_QUERYSTRING_AUTH = False

# Do not override file names
AWS_S3_FILE_OVERWRITE = False

AWS_S3_CUSTOM_DOMAIN = "media.torchbox.com"

AWS_STORAGE_BUCKET_NAME = "test"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
]

WAGTAILADMIN_BASE_URL = "http://example.com"
