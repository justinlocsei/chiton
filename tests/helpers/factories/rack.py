import factory
from factory.django import DjangoModelFactory
from faker import Faker

from chiton.rack.models import AffiliateNetwork

fake = Faker()


class AffiliateNetworkFactory(DjangoModelFactory):

    name = factory.LazyAttribute(lambda m: fake.sentence())
    slug = factory.Sequence(lambda n: '%s-%d' % (fake.word(), n))

    class Meta:
        model = AffiliateNetwork
