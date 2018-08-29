from storages.backends.s3boto3 import S3Boto3Storage


class S3Boto3StorageForWagtailDocument(S3Boto3Storage):
    # Enable signing.
    querystring_auth = True
    querystring_expire = 60

    # Signing URLs does not work with custom domains.
    custom_domain = None
