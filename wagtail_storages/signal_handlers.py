import functools
import logging

from django.db.models.signals import post_save

from wagtail.contrib.frontend_cache.utils import PurgeBatch
from wagtail.core.models import Collection
from wagtail.documents.models import get_document_model

from wagtail_storages.utils import (
    get_frontend_cache_configuration,
    is_s3_boto3_storage_used,
)

Document = get_document_model()

logger = logging.getLogger(__name__)


def skip_if_s3_storage_not_used(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not is_s3_boto3_storage_used():
            return
        return func(*args, **kwargs)

    return wrapper


@skip_if_s3_storage_not_used
def update_document_s3_acls_when_collection_saved(sender, instance, **kwargs):
    if not is_s3_boto3_storage_used():
        return
    if instance.get_view_restrictions():
        acl = "private"
    else:
        acl = "public-read"
    documents = Document.objects.filter(collection=instance)
    for document in documents:
        logger.debug(
            'Collection "%s" saved, set ACL to "%s" on "%s"',
            instance.name,
            acl,
            document.file.name,
        )
        document.file.file.obj.Acl().put(ACL=acl)


@skip_if_s3_storage_not_used
def update_document_s3_acls_when_document_saved(sender, instance, **kwargs):
    if not is_s3_boto3_storage_used():
        return
    if instance.collection.get_view_restrictions():
        acl = "private"
    else:
        acl = "public-read"
    instance.file.file.obj.Acl().put(ACL=acl)
    logger.debug('Document saved, set ACL to "%s" on "%s"', acl, instance.file.name)


@skip_if_s3_storage_not_used
def purge_document_from_cache_when_saved(sender, instance, **kwargs):
    if not is_s3_boto3_storage_used():
        return
    # No need for check if they are public or private - if they've changed,
    # they should be out of cache.
    logger.debug('Document "%s" saved, purge from cache', instance.file.name)
    if get_frontend_cache_configuration():
        s3_batch = PurgeBatch()
        s3_batch.add_url(instance.file.url)
        s3_batch.purge(backend_settings=get_frontend_cache_configuration())

    # Purge Wagtail document view URL using normal site's cache.
    wagtail_batch = PurgeBatch()
    wagtail_batch.add_url(instance.url)
    wagtail_batch.purge()


@skip_if_s3_storage_not_used
def purge_documents_when_collection_saved_with_restrictions(sender, instance, **kwargs):
    if not is_s3_boto3_storage_used():
        return
    # Do not purge documents if they are in a public collection.
    if not instance.get_view_restrictions():
        logger.debug(
            'Collection "%s" saved, don\'t purge from cache because it has '
            "no view restriction",
            instance.name,
        )
        return
    logger.debug(
        'Collection "%s" saved, has restrictions, purge its documents from '
        "the cache",
        instance.name,
    )
    # Purge download URLs and actual files if they possibly used to be public.
    wagtail_batch = PurgeBatch()
    s3_batch = PurgeBatch()
    for document in Document.objects.filter(collection=instance):
        wagtail_batch.add_url(document.url)
        s3_batch.add_url(document.file.url)
    wagtail_batch.purge()
    if get_frontend_cache_configuration():
        s3_batch.purge(backend_settings=get_frontend_cache_configuration())


def register_signal_handlers():
    # Updating S3 ACL.
    post_save.connect(
        update_document_s3_acls_when_collection_saved,
        sender=Collection,
        dispatch_uid="wagtail_storages_update_document_s3_acls_when_collection_saved",
    )
    post_save.connect(
        update_document_s3_acls_when_document_saved,
        sender=Document,
        dispatch_uid="wagtail_storages_update_document_s3_acls_when_document_saved",
    )
    # Front-end cache invalidation.
    post_save.connect(
        purge_document_from_cache_when_saved,
        sender=Document,
        dispatch_uid="wagtail_storages_purge_document_from_cache_when_saved",
    )
    post_save.connect(
        purge_documents_when_collection_saved_with_restrictions,
        sender=Collection,
        dispatch_uid=(
            "wagtail_storages_purge_documents_when_collection_saved_with_restrictions",
        ),
    )
