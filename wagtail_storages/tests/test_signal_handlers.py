from unittest.mock import MagicMock

from django.test import TestCase, override_settings

from wagtail_storages.signal_handlers import (
    skip_if_frontend_cache_invalidator_not_configured,
    skip_if_s3_storage_not_used,
)


class TestDecorators(TestCase):
    @override_settings(
        DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage"
    )
    def test_skipping_s3_storage_decorator_with_non_s3_storage(self):
        mock = MagicMock()
        skip_if_s3_storage_not_used(mock)()
        mock.assert_not_called()

    def test_skipping_s3_storage_decorator_with_s3_storage(self):
        mock = MagicMock()
        skip_if_s3_storage_not_used(mock)()
        mock.assert_called_once()

    @override_settings(WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE={})
    def test_skipping_frontend_purging_without_configuration(self):
        mock = MagicMock()
        skip_if_frontend_cache_invalidator_not_configured(mock)()
        mock.assert_not_called()

    @override_settings(
        WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE={
            "varnish": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                "LOCATION": "http://localhost:8000",
            },
        }
    )
    def test_purge_handlers_called_when_frontend_cache_configured(self):
        mock = MagicMock()
        skip_if_frontend_cache_invalidator_not_configured(mock)()
        mock.assert_called_once()
