import factory
from factory.django import DjangoModelFactory, ImageField
from faker import Faker

from .closet import GarmentFactory, StandardSizeFactory
from chiton.rack.models import AffiliateItem, AffiliateNetwork, ItemImage, StockRecord

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


class ItemImageFactory(DjangoModelFactory):

    item = factory.SubFactory(AffiliateItemFactory)
    file = ImageField(width=100, height=100)
    height = 100
    width = 100

    class Meta:
        model = ItemImage


def item_image_factory(affiliate_item_factory):
    def create_item_image(item=None, file=None, height=100, width=100):
        factory_kwargs = {
            'height': height,
            'width': width,
        }

        if item is not None:
            factory_kwargs['item'] = item

        if file is None:
            factory_kwargs['file__height'] = height
            factory_kwargs['file__width'] = width
        else:
            factory_kwargs['file'] = file

        return ItemImageFactory(**factory_kwargs)

    return create_item_image

    class Meta:
        model = ItemImage


class StockRecordFactory(DjangoModelFactory):

    item = factory.SubFactory(AffiliateItemFactory)
    size = factory.SubFactory(StandardSizeFactory)

    class Meta:
        model = StockRecord
