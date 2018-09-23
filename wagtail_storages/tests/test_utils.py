import django

from wagtail_storages import utils


class TestIsS3Boto3StorageUsed(django.test.TestCase):
    @django.test.override_settings(
        DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
    )
    def test_should_return_false_if_not(self):
        self.assertIs(
            utils.is_s3_boto3_storage_used(),
            False
        )

    @django.test.override_settings(
        DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage'
    )
    def test_should_return_true_if_yes(self):
        self.assertIs(
            utils.is_s3_boto3_storage_used(),
            True
        )
