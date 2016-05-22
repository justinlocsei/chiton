import factory
from factory.django import DjangoModelFactory
from faker import Faker

from .runway import BasicFactory
from chiton.closet.models import Brand, CanonicalSize, Garment

fake = Faker()


class BrandFactory(DjangoModelFactory):

    name = factory.LazyAttribute(lambda m: fake.company())

    class Meta:
        model = Brand


class CanonicalSizeFactory(DjangoModelFactory):

    name = factory.Sequence(lambda n: '%s-%d' % (fake.word(), n))
    range_lower = factory.Sequence(lambda n: n)
    range_upper = factory.Sequence(lambda n: n)

    class Meta:
        model = CanonicalSize


class GarmentFactory(DjangoModelFactory):

    name = factory.LazyAttribute(lambda m: '%s %s' % (fake.color_name(), fake.word()))
    brand = factory.SubFactory(BrandFactory)
    basic = factory.SubFactory(BasicFactory)

    class Meta:
        model = Garment
