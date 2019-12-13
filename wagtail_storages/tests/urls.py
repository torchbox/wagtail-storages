from django.urls import include, path

from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("documents/", include(wagtaildocs_urls)),
]
