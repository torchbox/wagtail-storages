from django.conf import settings
from django.core.files.storage import get_storage_class

import storages.backends.s3boto3


def is_s3_boto3_storage_used():
    return issubclass(get_storage_class(), storages.backends.s3boto3.S3Boto3Storage,)


def get_frontend_cache_configuration():
    return getattr(settings, "WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE", {})
