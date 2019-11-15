from urllib.parse import urlparse

from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from wagtail.core.models import Collection

import boto3
from moto import mock_s3

from wagtail_storages.factories import CollectionViewRestrictionFactory, DocumentFactory


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

    def check_document_is_public(self, document):
        all_users = 'http://acs.amazonaws.com/groups/global/AllUsers'
        # Loop over all the grants.
        for grant in document.file.file.obj.Acl().grants:
            # Find the all users grantee.
            if 'URI' not in grant['Grantee']:
                continue
            if grant['Grantee']['URI'] == all_users:
                if grant['Permission'] == 'READ':
                    return True
        return False

    def setUp(self):
        # Create S3 bucket
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        conn = boto3.resource('s3', region_name='eu-west-1')
        conn.create_bucket(Bucket=bucket_name)

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
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response.url)
        # Check object is public
        self.assertTrue(self.check_document_is_public(document))

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
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response.url)
        # Check object is not public
        self.assertFalse(self.check_document_is_public(document))
