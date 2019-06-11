from wagtail.core.models import Collection, CollectionViewRestriction
from wagtail.documents.models import Document

import factory
import factory.django


class DocumentFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'document' + str(n))
    file = factory.django.FileField(
        filename="testfile.txt",
        data=b'Test document',
    )

    class Meta:
        model = Document


class CollectionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'Collection' + str(n))
    depth = 0

    class Meta:
        model = Collection


class CollectionViewRestrictionFactory(factory.django.DjangoModelFactory):
    collection = factory.SubFactory(CollectionFactory)
    restriction_type = CollectionViewRestriction.PASSWORD
    password = 'password'

    class Meta:
        model = CollectionViewRestriction
