from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class WagtailStoragesConfig(AppConfig):
    name = 'wagtail_storages'
    verbose_name = _('Wagtail storages')

    def ready(self):
        from . import signals  # noqa
