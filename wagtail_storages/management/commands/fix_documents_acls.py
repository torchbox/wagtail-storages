from django.core.files.storage import get_storage_class
from django.core.management.base import BaseCommand, CommandError

from wagtail.core.models import Collection
from wagtail.documents import get_document_model

from storages.backends.s3boto3 import S3Boto3Storage

Document = get_document_model()


class Command(BaseCommand):
    help = 'blabla'

    def handle(self, *args, **options):
        if not issubclass(get_storage_class(), S3Boto3Storage):
            raise CommandError("You need to use S3Boto3Storage")
        for collection in Collection.objects.all():
            if collection.get_view_restrictions():
                acl = 'private'
            else:
                acl = 'public'
            documents = Document.objects.filter(collection=collection)
            for document in documents:
                document.obj.Acl().put(ACL=acl)
