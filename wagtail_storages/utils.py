import logging

from django.conf import settings
from django.core.files.storage import get_storage_class

from wagtail.documents.models import get_document_model

import storages.backends.s3boto3

logger = logging.getLogger(__name__)


def update_document_acl(document):
    if document.collection.get_view_restrictions():
        acl = "private"
    else:
        acl = "public-read"
    document.file.file.obj.Acl().put(ACL=acl)
    logger.debug('Set document ACL to "%s" on "%s"', acl, document.file.name)


def update_collection_document_acls(collection):
    if collection.get_view_restrictions():
        acl = "private"
    else:
        acl = "public-read"
    documents = get_document_model().objects.filter(collection=collection)
    for document in documents:
        logger.debug(
            'Set document ACL to "%s" on "%s"', acl, document.file.name,
        )
        document.file.file.obj.Acl().put(ACL=acl)


def is_s3_boto3_storage_used():
    return issubclass(get_storage_class(), storages.backends.s3boto3.S3Boto3Storage,)


def get_frontend_cache_configuration():
    return getattr(settings, "WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE", {})
