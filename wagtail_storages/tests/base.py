from django.conf import settings

import boto3
from moto import mock_s3


@mock_s3
class CreateBucket:
    def setUp(self):
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        conn = boto3.resource("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=bucket_name)
        super().setUp()
