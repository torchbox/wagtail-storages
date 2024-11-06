.. image:: https://github.com/torchbox/wagtail-storages/raw/main/images/logo.png

wagtail-storages
================

.. image:: https://img.shields.io/pypi/v/wagtail-storages.svg
   :target: https://pypi.org/project/wagtail-storages/
.. image:: https://img.shields.io/pypi/dm/wagtail-storages.svg
   :target: https://pypi.org/project/wagtail-storages/
.. image:: https://github.com/torchbox/wagtail-storages/actions/workflows/test.yml/badge.svg?branch=main
   :target: https://github.com/torchbox/wagtail-storages/actions/workflows/test.yml
   :alt: Build Status

This package fills the missing gap in using AWS S3 together with Wagtail. This
package will be useful if you want to:

- Use AWS S3 bucket for hosting Wagtail documents.
- Put the bucket behind the CDN so that the bucket is not called directly each
  time.
- Allow editors to use privacy controls on documents, whilst using CDN.
- Avoid time-outs because of downloads being proxied through Wagtail views.

  *Note: you cannot use the document* `redirect view`__ *if you want your documents to be truly private.*

.. _WagtailRedirectView: https://docs.wagtail.io/en/stable/advanced_topics/settings.html#wagtaildocs-serve-method
__ WagtailRedirectView_


What does it do?
----------------

The package is a collection of signal handlers and Wagtail hooks.

- Sets per-object ACLs on S3 whenever privacy settings change on a Wagtail
  document.
- Replaces the current document view with a redirect. Either to a signed S3
  bucket URL for private documents or public custom domain URL for public ones.
- Purges CDN for documents that have changed.

Requirements
------------

- ``django-storages`` with the ``S3Boto3Storage`` storage backend configured in
  a Wagtail project.
- CDN supported by Wagtail front-end cache invalidator.

Management commands
-------------------

``django-admin fix_document_acls``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The package provider a management command that sets all the documents' ACLs
according to the their collection permissions. This must be called if there had
been documents in a bucket before the package was used to make sure the ACLs in
the bucket are correct.

Settings
--------

WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the same format as Wagtail's ``WAGTAILFRONTENDCACHE`` setting, but to be
only used by the wagtail-storages to purge the documents. If not set, the purge
won't happen. `Read more on how to format it in the Wagtail docs
<https://docs.wagtail.io/en/stable/reference/contrib/frontendcache.html>`_,
e.g.


.. code:: python

   WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE = {
       'cloudfront': {
           'BACKEND': 'wagtail.contrib.frontend_cache.backends.CloudfrontBackend',
           'DISTRIBUTION_ID': 'your-distribution-id',
        },
   }

WAGTAIL_STORAGES_DOCUMENT_HOOK_ORDER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set a custom order for the document hook order. It's set to 100 by default.
It's important that it runs after any of your hooks since it returns a
response, e.g.

.. code:: python

   WAGTAIL_STORAGES_DOCUMENT_HOOK_ORDER = 900


Recommended S3 setup with Wagtail
---------------------------------

The following guide explains the recommended setup for using S3 with Wagtail.
This guide assumes that:

* You serve your main website at ``llamasavers.com`` (replace
  ``llamasavers.com`` with your actual domain name).
* Your S3 bucket is called ``media.llamasavers.com`` and you host it from that
  domain name.
* You are using CDN on that domain, this guide will assume Cloudflare.

Set up S3 bucket
~~~~~~~~~~~~~~~~

First, set up your S3 bucket. It must be configured to:

- Have a name that matches the domain name, e.g. ``media.llamasavers.com``.
- Allow the user to perform the following actions on the bucket:
   - ``s3:ListBucket``
   - ``s3:GetBucketLocation``
   - ``s3:ListBucketMultipartUploads``
   - ``s3:ListBucketVersions``
- Allow the user to perform all the actions (``s3:*``) on the objects within the
  bucket.
- Allow the internet traffic to access Wagtail image renditions (``images/*``).
- Allow use of public ACLs, by setting up the following Block public access:
   - Deselect "Block public access to buckets and objects granted through new access control lists (ACLs)"
   - Deselect "Block public access to buckets and objects granted through any access control lists (ACLs)"
   - Select "Block public access to buckets and objects granted through new public bucket or access point policies"
   - Select "Block public and cross-account access to buckets and objects through any public bucket or access point policies"

.. image:: images/s3-block-public-access.png


The user permissions can be set in the IAM or via a bucket policy. See example
of all of those points being achieved in the bucket policy below.

.. code:: json

   {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::[BUCKET NAME]/images/*"
            },
            {
                "Sid": "AllowUserManageBucket",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::[USER ARN]"
                },
                "Action": [
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                    "s3:ListBucketMultipartUploads",
                    "s3:ListBucketVersions"
                ],
                "Resource": "arn:aws:s3:::[BUCKET NAME]"
            },
            {
                "Sid": "AllowUserManageBucketObjects",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::[USER ARN]"
                },
                "Action": "s3:*",
                "Resource": "arn:aws:s3:::[BUCKET NAME]/*"
            }
        ]
    }


After the S3 bucket is set up on AWS, you can configure the Wagtail project to
use it.

Set up django-storages
~~~~~~~~~~~~~~~~~~~~~~

Install ``django-storages`` and ``boto3``.

.. code:: sh

   pip install django-storages[boto3]

Set up your S3 bucket with ``django-storages``. The following code allows
configuration via environment variables.

.. code:: python

    # settings.py
    import os


    if "AWS_STORAGE_BUCKET_NAME" in os.environ:
        # Add django-storages to the installed apps
        INSTALLED_APPS = INSTALLED_APPS + ["storages"]

        # https://docs.djangoproject.com/en/stable/ref/settings/#default-file-storage
        DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

        AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]

        # Disables signing of the S3 objects' URLs. When set to True it
        # will append authorization querystring to each URL.
        AWS_QUERYSTRING_AUTH = False

        # Do not allow overriding files on S3 as per Wagtail docs recommendation:
        # https://docs.wagtail.io/en/stable/advanced_topics/deploying.html#cloud-storage
        # Not having this setting may have consequences such as losing files.
        AWS_S3_FILE_OVERWRITE = False

        # Default ACL for new files should be "private" - not accessible to the
        # public. Images should be made available to public via the bucket policy,
        # where the documents should use wagtail-storages.
        AWS_DEFAULT_ACL = "private"

        # We generally use this setting in production to put the S3 bucket
        # behind a CDN using a custom domain, e.g. media.llamasavers.com.
        # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#cloudfront
        if "AWS_S3_CUSTOM_DOMAIN" in os.environ:
            AWS_S3_CUSTOM_DOMAIN = os.environ["AWS_S3_CUSTOM_DOMAIN"]

        # When signing URLs is enabled, the region must be set.
        # The global S3 endpoint does not seem to support signed URLS.
        # Set this only if you will be using signed URLs.
        if "AWS_S3_REGION_NAME" in os.environ:
            AWS_S3_REGION_NAME = os.environ["AWS_S3_REGION_NAME"]

        # This settings lets you force using http or https protocol when generating
        # the URLs to the files. Set https as default.
        # https://github.com/jschneier/django-storages/blob/10d1929de5e0318dbd63d715db4bebc9a42257b5/storages/backends/s3boto3.py#L217
        AWS_S3_URL_PROTOCOL = os.environ.get("AWS_S3_URL_PROTOCOL", "https:")


If you use the above snippet, you can set the following environment variables:

* ``AWS_STORAGE_BUCKET_NAME`` - set to ``media.llamasavers.com``.
* ``AWS_S3_CUSTOM_DOMAIN`` - set to ``media.llamasavers.com``.
* ``AWS_S3_REGION_NAME`` - set to your AWS region name, e.g. ``eu-west-2``.

You can use one of the methods to provide `boto3 with credentials`__. We
suggest you stick with the environment variables. To do that, you need to set
the following variables:

* ``AWS_ACCESS_KEY_ID``
* ``AWS_SECRET_ACCESS_KEY``

.. _Boto3Credentials: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

__ Boto3Credentials_

Now the storage should be configured and working. Editors should be able to
upload images and documents in Wagtail admin.

Set up ``wagtail-storages``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install ``wagtail-storages`` itself.

.. code:: sh

   pip install wagtail-storages


Add ``wagtail_storages`` to your ``INSTALLED_APPS`` in your settings file.

.. code:: python

   # settings.py

   INSTALLED_APPS = [
       # ... Other apps
       "wagtail_storages.apps.WagtailStoragesConfig",
       # ... Other apps
   ]

With that, ACLs should be updated if documents are moved to
private collections.

If you already have files in your S3 bucket, run ``django-admin
fix_document_acls`` to make sure all documents have the right ACLs set up.

Set up front-end cache invalidation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If edge cache is set up on the custom domain (``media.llamasavers.com``) you
should set up the CDN purging to avoid having outdated or private documents
available to users via the CDN endpoint. For example, for Cloudflare you want
to use a configuration similar to the one below:

.. code:: python

   # settings.py
   import os


   if "S3_CACHE_CLOUDFLARE_TOKEN" in os.environ:
        WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE = {
            "default": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.CloudflareBackend",
                "EMAIL": os.environ["S3_CACHE_CLOUDFLARE_EMAIL"],
                "TOKEN": os.environ["S3_CACHE_CLOUDFLARE_TOKEN"],
                "ZONEID": os.environ["S3_CACHE_CLOUDFLARE_ZONEID"],
            },
        }

Then set the following environment variables:

* ``S3_CACHE_CLOUDFLARE_EMAIL``
* ``S3_CACHE_CLOUDFLARE_TOKEN``
* ``S3_CACHE_CLOUDFLARE_ZONEID``

Once set up, the documents will be purged from cache when they are
modified or their privacy settings have changed.

The setting follows configuration format of the front-end cache invalidator
configuration in Wagtail. See the details `here`__. The only difference is
the setting name, which for wagtail-storages is
``WAGTAIL_STORAGES_DOCUMENTS_FRONTENDCACHE``.

.. _WagtailFrontEndCache: https://docs.wagtail.io/en/stable/reference/contrib/frontendcache.html

__ WagtailFrontEndCache_

All done!
