import factory
from factory.django import DjangoModelFactory
from faker import Faker

from .runway import BasicFactory
from chiton.closet.models import Brand, Garment

fake = Faker()


class BrandFactory(DjangoModelFactory):

    name = factory.LazyAttribute(lambda m: fake.company())

    class Meta:
        model = Brand


class GarmentFactory(DjangoModelFactory):

    name = factory.LazyAttribute(lambda m: '%s %s' % (fake.color_name(), fake.word()))
    brand = factory.SubFactory(BrandFactory)
    basic = factory.SubFactory(BasicFactory)

    class Meta:
        model = Garment
