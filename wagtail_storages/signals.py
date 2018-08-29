import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from wagtail.contrib.frontend_cache.utils import PurgeBatch
from wagtail.core.models import Collection
from wagtail.documents.models import get_document_model

from .utils import is_s3_boto3_storage_used

Document = get_document_model()

logger = logging.getLogger(__name__)


def update_document_s3_acls_when_collection_saved(sender, instance, **kwargs):
    if instance.get_view_restrictions():
        acl = 'private'
    else:
        acl = 'public-read'
    documents = Document.objects.filter(collection=instance)
    for document in documents:
        logger.debug(
            'Collection saved, set ACL to "%s" on "%s"',
            acl,
            document.file.name
        )
        document.file.file.obj.Acl().put(ACL=acl)


def update_document_s3_acls_when_document_saved(sender, instance, **kwargs):
    if instance.collection.get_view_restrictions():
        acl = 'private'
    else:
        acl = 'public-read'
    instance.file.file.obj.Acl().put(ACL=acl)
    logger.debug(
        'Document saved, set ACL to "%s" on "%s"', acl, instance.file.name
    )


def purge_document_from_cache_when_saved(sender, instance, **kwargs):
    logger.debug('Document "%s" saved, purge from cache', instance.file.name)
    batch = PurgeBatch()
    batch.add_url(instance.url)
    batch.add_url(instance.file.url)
    batch.purge()


@receiver(post_save, sender=Collection)
def purge_documents_when_collection_saved_with_restrictions(sender, instance,
                                                            **kwargs):
    if not instance.get_view_restrictions():
        logger.debug(
            'Collection "%s" saved, don\'t purge from cache because it has '
            'no view restriction',
            instance.name
        )
        return
    logger.debug(
        'Collection "%s" saved, has restrictions, purge its documents from '
        'the cache', instance.name
    )
    batch = PurgeBatch()
    for document in Document.objects.filter(collection=instance):
        batch.add_url(document.url)
        batch.add_url(document.file.url)
    batch.purge()


if is_s3_boto3_storage_used():
    post_save.connect(
        update_document_s3_acls_when_collection_saved, sender=Collection
    )
    post_save.connect(
        update_document_s3_acls_when_document_saved, sender=Document
    )
    post_save.connect(purge_document_from_cache_when_saved, sender=Document)
    post_save.connect(
        purge_documents_when_collection_saved_with_restrictions,
        sender=Collection
    )
    post_save.connect(
        purge_documents_when_collection_saved_with_restrictions,
        sender=Collection
    )
