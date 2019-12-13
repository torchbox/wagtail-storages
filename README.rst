wagtail-storages
================

This package helps to maintain Wagtail documents hosted on S3.

**This is currently only proof of concept. Do not use on the production.**

Features
--------

- Serve public documents straight from S3.
- Service private documents straight from S3 using signed URLs.
- Purge documents from front-end cache when needed.

Requirements
------------

- You use ``django-storages`` with ``S3Boto3Storage`` as your storage backend
  and you have configured it.
- Your S3 user can set files' ACLs in the bucket you use.
- Front-end cache purging uses Wagtail's ``frontendcache`` contrib module, so
  you need to configure that beforehand.
- You don't cache your Wagtail's documents view, since that would make it
  impossible to have private files.
- ``AWS_QUERYSTRING_AUTH = False`` is set if you want to serve public files
  without querystring auth.

Rationale
---------

The reason this package was developed is that currently Wagtail has to read all
of your file in the Python view and return it from Python. It turns out to be
fairly inefficient and may result in long response times. Also there's no
solution out there to efficiently serve private files from Wagtail and S3.

Management command
------------------

There's a management command that sets all the documents' ACLs according to the
their collection permissions. This may be useful if you started using
wagtail-storages after you uploaded documents.

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
