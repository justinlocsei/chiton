import factory
from factory.django import DjangoModelFactory
from faker import Faker

from chiton.runway.data import PROPRIETY_IMPORTANCE_CHOICES
from chiton.runway.models import Basic, Category, Formality, Propriety, Style

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


class ProprietyFactory(DjangoModelFactory):

    basic = factory.SubFactory(BasicFactory)
    formality = factory.SubFactory(FormalityFactory)
    importance = factory.Sequence(lambda n: PROPRIETY_IMPORTANCE_CHOICES[n % (len(PROPRIETY_IMPORTANCE_CHOICES) - 1)][0])

    class Meta:
        model = Propriety


class StyleFactory(DjangoModelFactory):

    name = factory.Sequence(lambda n: '%s-%d' % (fake.sentence(), n))

    class Meta:
        model = Style
