from django.shortcuts import redirect
from django.utils.cache import add_never_cache_headers

from wagtail.core import hooks
from wagtail.documents.models import document_served, get_document_model

from .backends import S3Boto3StorageForWagtailDocument
from .utils import is_s3_boto3_storage_used


@hooks.register('before_serve_document', order=100)
def serve_document_from_s3(document, request):
    # Skip this hook if not using django-storages boto3 backend.
    if not is_s3_boto3_storage_used():
        return

    # Send document_served signal.
    document_served.send(sender=get_document_model(), instance=document,
                         request=request)

    # If document has restrictions, generate a signed URL, otherwise
    # return its public URL.
    if document.collection.get_view_restrictions():
        file_url = S3Boto3StorageForWagtailDocument().url(document.file.name)
    else:
        file_url = document.file.url

    # Generate redirect response and add never_cache headers.
    response = redirect(file_url)
    del response['Cache-control']
    add_never_cache_headers(response)
    return response
