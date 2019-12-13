from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings


class TestFixDocumentAcls(TestCase):
    def test_call_does_not_fail(self):
        call_command("fix_document_acls")

    @override_settings(
        DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage"
    )
    def test_call_fails_when_s3_boto3_storage_not_used(self):
        with self.assertRaisesRegex(
            CommandError,
            "Your storage needs to be set to S3Boto3Storage in order to use "
            "this command.",
        ):
            call_command("fix_document_acls")
