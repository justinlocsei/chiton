import factory
from factory.django import DjangoModelFactory
from faker import Faker

from .closet import GarmentFactory, StandardSizeFactory
from chiton.rack.models import AffiliateItem, AffiliateNetwork, ProductImage, StockRecord

fake = Faker()


class AffiliateNetworkFactory(DjangoModelFactory):

    name = factory.LazyAttribute(lambda m: fake.sentence())
    slug = factory.Sequence(lambda n: '%s-%d' % (fake.word(), n))

    class Meta:
        model = AffiliateNetwork


class AffiliateItemFactory(DjangoModelFactory):

    network = factory.SubFactory(AffiliateNetworkFactory)
    url = factory.LazyAttribute(lambda m: fake.url())
    name = factory.LazyAttribute(lambda m: fake.sentence())
    guid = factory.Sequence(lambda m: fake.uuid4())
    garment = factory.SubFactory(GarmentFactory)

    class Meta:
        model = AffiliateItem


class ProductImageFactory(DjangoModelFactory):

    url = factory.LazyAttribute(lambda m: fake.url())
    height = 100
    width = 100

    class Meta:
        model = ProductImage


class StockRecordFactory(DjangoModelFactory):

    item = factory.SubFactory(AffiliateItemFactory)
    size = factory.SubFactory(StandardSizeFactory)

    class Meta:
        model = StockRecord
