from django.core.files.storage import get_storage_class
from django.db.models.signals import post_save
from django.dispatch import receiver

from wagtail.contrib.frontend_cache.utils import PurgeBatch
from wagtail.core.models import Collection
from wagtail.documents import get_document_model

from storages.backends.s3boto3 import S3Boto3Storage

Document = get_document_model()


@receiver(post_save, sender=Collection)
def update_document_s3_acls_when_collection_saved(sender, instance, **kwargs):
    if not issubclass(get_storage_class(), S3Boto3Storage):
        return
    if instance.get_view_restrictions():
        acl = 'private'
    else:
        acl = 'public'
    documents = Document.objects.filter(collection=instance)
    for document in documents:
        document.file.obj.Acl().put(ACL=acl)


@receiver(post_save, sender=Document)
def update_document_s3_acls_when_document_saved(sender, instance, **kwargs):
    if not issubclass(get_storage_class(), S3Boto3Storage):
        return
    if instance.collection.get_view_restrictions():
        acl = 'private'
    else:
        acl = 'public'
    instance.file.obj.Acl().put(ACL=acl)


@receiver(post_save, sender=Document)
def purge_document_from_cache_when_saved(sender, instance, **kwargs):
    batch = PurgeBatch()
    batch.add_url(instance.url)
    batch.add_url(instance.file.url)
    batch.purge()


@receiver(post_save, sender=Collection)
def purge_documents_when_collection_saved_with_restrictions(sender, instance,
                                                            **kwargs):
    if not instance.get_view_restrictions():
        return
    batch = PurgeBatch()
    for document in Document.objects.filter(collection=instance):
        batch.add_url(document.url)
        batch.add_url(document.file.url)
    batch.purge()
