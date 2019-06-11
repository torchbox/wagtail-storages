from urllib.parse import urlparse

from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse

from wagtail.core.models import Collection

import boto3
from moto import mock_s3

from ..factories import CollectionViewRestrictionFactory, DocumentFactory


@override_settings(
    DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage',
    AWS_STORAGE_BUCKET_NAME='test',
)
@mock_s3
class AmazonS3DocumentTests(TestCase):
    def check_s3_url(self, url):
        return 's3.amazonaws.com' in url

    def check_url_signed(self, url):
        parsed_url = urlparse(url)
        query_args = [
            'AWSAccessKeyId',
            'Signature',
            'Expires',
        ]
        for query_arg in query_args:
            if query_arg not in parsed_url.query:
                return False
        return True

    def setUp(self):
        # Create S3 bucket
        conn = boto3.resource('s3', region_name='eu-west-1')
        conn.create_bucket(Bucket='test')

        self.client = Client()
        self.root_collection = Collection.get_first_root_node()
        self.private_collection = self.root_collection.add_child(
            name='Restricted collection',
        )
        self.private_collection_restriction = CollectionViewRestrictionFactory(collection=self.private_collection) # noqa
        self.view_restriction_session_key = self.private_collection_restriction.passed_view_restrictions_session_key # noqa

    def test_create_public_document(self):
        # Create document.
        document = DocumentFactory()

        # Check the document is on amazon's servers.
        self.assertTrue(self.check_s3_url(document.file.url))

        # Load the document
        url = reverse(
            'wagtaildocs_serve',
            args=(document.id, document.filename),
        )
        response = self.client.get(url)

        # Test wagtail redirects to S3.
        self.assertTrue(response.url)
        # Check the url given wasn't signed.
        self.assertFalse(self.check_url_signed(response.url))

    def test_create_private_document(self):
        # Create document.
        document = DocumentFactory()
        # Add the document to the private collection.
        document.collection = self.private_collection
        document.save()

        # Check the document is on amazon's servers.
        self.assertTrue(self.check_s3_url(document.file.url))

        # Authorise the session.
        s = self.client.session
        s.update({
            self.view_restriction_session_key: [self.private_collection_restriction.id], # noqa
        })
        s.save()

        # Load the document
        url = reverse(
            'wagtaildocs_serve',
            args=(document.id, document.filename),
        )
        response = self.client.get(url)

        # Test wagtail redirects to S3.
        self.assertTrue(response.url)
        # Check the url given was signed.
        self.assertTrue(self.check_url_signed(response.url))
