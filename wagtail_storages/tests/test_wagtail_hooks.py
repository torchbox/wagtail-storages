from urllib.parse import urlparse

from django.test import RequestFactory, TestCase, override_settings

from moto import mock_s3

from wagtail_storages.factories import CollectionViewRestrictionFactory, DocumentFactory
from wagtail_storages.wagtail_hooks import serve_document_from_s3


@mock_s3
class TestWagtailHooks(TestCase):
    @override_settings(
        DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage"
    )
    def test_non_s3_storage_returns_no_response(self):
        # The hook should not return a response if S3 storage is not being
        # used.
        document = DocumentFactory()
        request = RequestFactory().get(path=document.url)
        response = serve_document_from_s3(document, request)
        self.assertIsNone(response)

    def test_s3_storage_returns_response_for_public_file(self):
        # The hook should return default document URL for public documents
        # using S3.
        document = DocumentFactory()
        request = RequestFactory().get(path=document.url)
        response = serve_document_from_s3(document, request)
        self.assertEqual(response.status_code, 302)
        # Make sure it uses the default URL.
        self.assertEqual(response.url, document.file.url)

    def test_s3_storage_returns_response_for_private_files(self):
        # The hook should return document URL from the private document S3
        # backend.
        restriction = CollectionViewRestrictionFactory()
        document = DocumentFactory(collection=restriction.collection)
        request = RequestFactory().get(path=document.url)
        response = serve_document_from_s3(document, request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("amazonaws.com", urlparse(response.url).hostname)

    def test_redirect_response_is_never_cached(self):
        document = DocumentFactory()
        request = RequestFactory().get(path=document.url)
        response = serve_document_from_s3(document, request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("cache-control", response)
        self.assertEqual(
            response["cache-control"], "max-age=0, no-cache, no-store, must-revalidate"
        )
