from django.core.files.storage import get_storage_class

from storages.backends.s3boto3 import S3Boto3Storage


def is_s3_boto3_storage_used():
    return issubclass(get_storage_class(), S3Boto3Storage)
