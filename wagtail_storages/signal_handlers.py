import functools
import logging

from django.db.models.signals import post_save, pre_delete

from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.core.models import Collection

if WAGTAIL_VERSION < (2, 8):
    from wagtail.documents.models import get_document_model
else:
    from wagtail.documents import get_document_model

from wagtail_storages.utils import (
    is_s3_boto3_storage_used,
    purge_collection_documents_from_cache,
    purge_document_from_cache,
    update_collection_document_acls,
    update_document_acl,
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
def update_document_acls_when_collection_saved(sender, instance, **kwargs):
    update_collection_document_acls(instance)


@skip_if_s3_storage_not_used
def update_document_acls_when_document_saved(sender, instance, **kwargs):
    update_document_acl(instance)


@skip_if_s3_storage_not_used
def purge_document_from_cache_when_saved(sender, instance, **kwargs):
    purge_document_from_cache(instance)


@skip_if_s3_storage_not_used
def purge_document_from_cache_when_deleted(sender, instance, **kwargs):
    purge_document_from_cache(instance)


@skip_if_s3_storage_not_used
def purge_documents_when_collection_saved_with_restrictions(sender, instance, **kwargs):
    purge_collection_documents_from_cache(instance)


def register_signal_handlers():
    # Updating S3 ACL.
    post_save.connect(
        update_document_acls_when_collection_saved,
        sender=Collection,
        dispatch_uid="wagtail_storages_update_document_s3_acls_when_collection_saved",
    )
    post_save.connect(
        update_document_acls_when_document_saved,
        sender=Document,
        dispatch_uid="wagtail_storages_update_document_s3_acls_when_document_saved",
    )
    # Front-end cache invalidation.
    post_save.connect(
        purge_document_from_cache_when_saved,
        sender=Document,
        dispatch_uid="wagtail_storages_purge_document_from_cache_when_saved",
    )
    pre_delete.connect(
        purge_document_from_cache_when_deleted,
        sender=Document,
        dispatch_uid="wagtail_storages_purge_document_from_cache_when_deleted",
    )
    post_save.connect(
        purge_documents_when_collection_saved_with_restrictions,
        sender=Collection,
        dispatch_uid=(
            "wagtail_storages_purge_documents_when_collection_saved_with_restrictions",
        ),
    )
