wagtail-storages
================

This package helps to maintain Wagtail documents hosted on S3.

**This is currently only proof of concept. Do not use on the production.**

Features
-------

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

Rationale
---------

The reason this package was developed is that currently Wagtail has to read all
of your file in the Python view and return it from Python. It turns out to be
fairly inefficient and may result in long response times. Also there's no
solution out there to efficiently serve private files from Wagtail and S3.
