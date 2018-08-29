from django.core.management.base import BaseCommand, CommandError

from wagtail.core.models import Collection
from wagtail.documents.models import get_document_model

from wagtail_storages.utils import is_s3_boto3_storage_used


Document = get_document_model()


class Command(BaseCommand):
    help = "Fix documents' ACLs on S3 to match their collection settings"

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        if not is_s3_boto3_storage_used():
            raise CommandError(
                'Your storage needs to be set to S3Boto3Storage in order to '
                'use this command.'
            )
        for collection in Collection.objects.all():
            if collection.get_view_restrictions():
                acl = 'private'
            else:
                acl = 'public-read'
            if self.verbosity >= 1:
                self.stdout.write(
                    'Updating the "{}" collection\'s documents to "{}" '
                    'ACL.'.format(collection.name, acl)
                )
            documents = Document.objects.filter(collection=collection)
            for document in documents:
                if self.verbosity >= 2:
                    self.stdout.write(
                        'Updating the "{}" document\'s ACL to {}'.format(
                            document.file.name, acl
                        )
                    )
                document.file.file.obj.Acl().put(ACL=acl)
