from django.core.management.base import BaseCommand, CommandError

from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (3, 0):
    from wagtail.models import Collection
else:
    from wagtail.core.models import Collection

from wagtail_storages.utils import (
    is_s3_boto3_storage_used,
    update_collection_document_acls,
)


class Command(BaseCommand):
    help = "Fix documents' ACLs on S3 to match their collection settings"

    def handle(self, *args, **options):
        if not is_s3_boto3_storage_used():
            raise CommandError(
                "Your storage needs to be set to S3Boto3Storage in order to "
                "use this command."
            )
        for collection in Collection.objects.all():
            update_collection_document_acls(collection)
