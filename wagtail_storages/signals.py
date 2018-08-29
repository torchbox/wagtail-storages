from django.core.files.storage import get_storage_class
from django.db.models.signals import post_save

from wagtail.core.models import Collection
from wagtail.documents import get_document_model

from storages.backends.s3boto3 import S3Boto3Storage

Document = get_document_model()


def update_document_acls_when_collection_saved(sender, instance, **kwargs):
    if not issubclass(get_storage_class(), S3Boto3Storage):
        return
    if instance.get_view_restrictions():
        acl = 'private'
    else:
        acl = 'public'
    documents = Document.objects.filter(collection=instance)
    for document in documents:
        document.file.obj.Acl().put(ACL=acl)


post_save.connect(update_document_acls_when_collection_saved,
                  sender=Collection)


def update_document_acls_when_document_saved(sender, instance, **kwargs):
    if not issubclass(get_storage_class(), S3Boto3Storage):
        return
    if instance.collection.get_view_restrictions():
        acl = 'private'
    else:
        acl = 'public'
    instance.file.obj.Acl().put(ACL=acl)


post_save.connect(update_document_acls_when_document_saved, sender=Document)
