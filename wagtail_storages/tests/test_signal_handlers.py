from unittest import mock
from unittest.mock import MagicMock

from django.db.models.signals import post_save
from django.test import TestCase, override_settings

import factory
from moto import mock_s3

from wagtail_storages.factories import (
    CollectionFactory,
    CollectionViewRestrictionFactory,
    DocumentFactory,
)
from wagtail_storages.signal_handlers import (
    purge_document_from_cache_when_deleted,
    purge_document_from_cache_when_saved,
    purge_documents_when_collection_saved_with_restrictions,
    skip_if_s3_storage_not_used,
    update_document_acls_when_collection_saved,
    update_document_acls_when_document_saved,
)
from wagtail_storages.tests.utils import is_s3_object_is_public


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


@mock_s3
class TestUpdateDocumentAclsWhenCollectionSaved(TestCase):
    @factory.django.mute_signals(post_save)
    def test_s3_object_acl_set_to_public(self):
        document = DocumentFactory()
        collection = document.collection
        update_document_acls_when_collection_saved(
            sender=collection._meta.model, instance=collection
        )
        self.assertTrue(is_s3_object_is_public(document.file.file.obj))

    @factory.django.mute_signals(post_save)
    def test_s3_object_acl_set_to_private(self):
        private_collection = CollectionViewRestrictionFactory().collection
        document = DocumentFactory(collection=private_collection)
        update_document_acls_when_collection_saved(
            sender=private_collection._meta.model, instance=private_collection
        )
        self.assertFalse(is_s3_object_is_public(document.file.file.obj))


@mock_s3
class TestUpdateDocumentAclsWhenDocumentSaved(TestCase):
    @factory.django.mute_signals(post_save)
    def test_s3_object_acl_set_to_public(self):
        document = DocumentFactory()
        update_document_acls_when_document_saved(
            sender=document._meta.model, instance=document
        )
        self.assertTrue(is_s3_object_is_public(document.file.file.obj))

    @factory.django.mute_signals(post_save)
    def test_s3_object_acl_set_to_private(self):
        private_collection = CollectionViewRestrictionFactory().collection
        document = DocumentFactory(collection=private_collection)
        update_document_acls_when_document_saved(
            sender=document._meta.model, instance=document
        )
        self.assertFalse(is_s3_object_is_public(document.file.file.obj))


@mock_s3
class TestPurgeDocumentsWhenCollectionSavedWithRestrictions(TestCase):
    @override_settings(
        WAGTAILFRONTENDCACHE={
            "varnish": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                "LOCATION": "http://localhost:8000",
            },
        },
        WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE={
            "varnish": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                "LOCATION": "http://localhost:8000",
            },
        },
    )
    @factory.django.mute_signals(post_save)
    def test_cache_purged_for_private_collection(self):
        private_collection = CollectionViewRestrictionFactory().collection
        DocumentFactory(collection=private_collection)
        with mock.patch(
            "wagtail.contrib.frontend_cache.backends.urlopen"
        ) as urlopen_mock:
            purge_documents_when_collection_saved_with_restrictions(
                sender=private_collection._meta.model, instance=private_collection
            )
        urlopen_mock.assert_called()

    @override_settings(
        WAGTAILFRONTENDCACHE={
            "varnish": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                "LOCATION": "http://localhost:8000",
            },
        },
        WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE={
            "varnish": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                "LOCATION": "http://localhost:8000",
            },
        },
    )
    @factory.django.mute_signals(post_save)
    def test_cache_not_purged_for_public_collection(self):
        collection = CollectionFactory()
        DocumentFactory.create_batch(10, collection=collection)
        with mock.patch(
            "wagtail.contrib.frontend_cache.backends.urlopen"
        ) as urlopen_mock:
            purge_documents_when_collection_saved_with_restrictions(
                sender=collection._meta.model, instance=collection
            )
        urlopen_mock.assert_not_called()


@mock_s3
class TestPurgeDocumentFromCacheWhenSaved(TestCase):
    @override_settings(
        WAGTAILFRONTENDCACHE={
            "varnish": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                "LOCATION": "http://localhost:8000",
            },
        },
        WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE={
            "varnish": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                "LOCATION": "http://localhost:8000",
            },
        },
    )
    @factory.django.mute_signals(post_save)
    def test_create_new_document_purges_cache_for_that_url(self):
        document = DocumentFactory()
        with mock.patch(
            "wagtail.contrib.frontend_cache.backends.urlopen"
        ) as urlopen_mock:
            purge_document_from_cache_when_saved(
                sender=document._meta.model, instance=document
            )
        urlopen_mock.assert_called()

    @override_settings(
        WAGTAILFRONTENDCACHE={
            "varnish": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                "LOCATION": "http://localhost:8000",
            },
        },
        WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE={
            "varnish": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
                "LOCATION": "http://localhost:8000",
            },
        },
    )
    @factory.django.mute_signals(post_save)
    def test_delete_document_purges_cache_for_that_url(self):
        document = DocumentFactory()
        with mock.patch(
            "wagtail.contrib.frontend_cache.backends.urlopen"
        ) as urlopen_mock:
            purge_document_from_cache_when_deleted(
                sender=document._meta.model, instance=document
            )
        urlopen_mock.assert_called()
