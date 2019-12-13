from django.core.files.storage import get_storage_class
from django.test import TestCase

from storages.backends.s3boto3 import S3Boto3Storage

from wagtail_storages.backends import (
    get_private_s3_boto3_document_storage_backend_class,
)


class TestGetPrivateBackendFunction(TestCase):
    def setUp(self):
        self.backend_class = get_private_s3_boto3_document_storage_backend_class()

    def test_returns_s3_boto_subclass(self):
        self.assertTrue(issubclass(self.backend_class, S3Boto3Storage))

    def test_backend_overrides_settings(self):
        private_backend = self.backend_class()

        default_backend = get_storage_class()()
        self.assertIsInstance(default_backend, S3Boto3Storage)

        # Make sure querystring authentication is enabled and custom domain is
        # disabled.
        self.assertTrue(private_backend.querystring_auth)
        self.assertIsNone(private_backend.custom_domain)

        self.assertFalse(default_backend.querystring_auth)
        self.assertEqual(default_backend.custom_domain, "media.torchbox.com")
        self.assertEqual(private_backend.default_acl, "private")
        self.assertEqual(default_backend.default_acl, "private")
