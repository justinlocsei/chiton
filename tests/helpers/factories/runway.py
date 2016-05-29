import factory
from factory.django import DjangoModelFactory
from faker import Faker

from chiton.runway.models import Basic, Category, Formality, Style

fake = Faker()


class CategoryFactory(DjangoModelFactory):

    name = factory.Sequence(lambda n: '%s-%d' % (fake.sentence(), n))

    class Meta:
        model = Category


class BasicFactory(DjangoModelFactory):

    name = factory.Sequence(lambda n: '%s-%d' % (fake.sentence(), n))
    category = factory.SubFactory(CategoryFactory)

    class Meta:
        model = Basic


class FormalityFactory(DjangoModelFactory):

    name = factory.LazyAttribute(lambda m: fake.word())
    position = factory.Sequence(lambda n: n)

    class Meta:
        model = Formality


class StyleFactory(DjangoModelFactory):

    name = factory.Sequence(lambda n: '%s-%d' % (fake.sentence(), n))

    class Meta:
        model = Style
