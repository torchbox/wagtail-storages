import django

import storages.backends.s3boto3


def is_s3_boto3_storage_used():
    return issubclass(
        django.core.files.storage.get_storage_class(),
        storages.backends.s3boto3.S3Boto3Storage
    )
