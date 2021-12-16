__version__ = "0.0.6"

import django

if django.VERSION >= (3, 2):
    # The declaration is only needed for older Django versions
    pass
else:
    default_app_config = "wagtail_storages.apps.WagtailStoragesConfig"
