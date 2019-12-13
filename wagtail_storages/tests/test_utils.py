from django.test import TestCase, override_settings

from wagtail_storages.factories import (
    CollectionFactory,
    CollectionViewRestrictionFactory,
)
from wagtail_storages.utils import (
    get_acl_for_collection,
    get_frontend_cache_configuration,
    is_s3_boto3_storage_used,
)


class TestIsS3Boto3StorageUsed(TestCase):
    @override_settings(
        DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage"
    )
    def test_should_return_false_if_not(self):
        self.assertIs(is_s3_boto3_storage_used(), False)

    @override_settings(DEFAULT_FILE_STORAGE="storages.backends.s3boto3.S3Boto3Storage")
    def test_should_return_true_if_yes(self):
        self.assertIs(is_s3_boto3_storage_used(), True)

    @override_settings(WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE={})
    def test_get_frontend_cache_configuration_1(self):
        self.assertEqual(get_frontend_cache_configuration(), {})

    @override_settings(
        WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE={
            "varnish": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                "LOCATION": "http://localhost:8000",
            },
        }
    )
    def test_get_frontend_cache_configuration_2(self):
        self.assertEqual(
            get_frontend_cache_configuration(),
            {
                "varnish": {
                    "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                    "LOCATION": "http://localhost:8000",
                },
            },
        )


class TestGetAclForCollection(TestCase):
    def test_public_colleciton(self):
        collection = CollectionFactory()
        self.assertEqual(get_acl_for_collection(collection), "public-read")

    def test_private_colleciton(self):
        collection = CollectionViewRestrictionFactory().collection
        self.assertEqual(get_acl_for_collection(collection), "private")
