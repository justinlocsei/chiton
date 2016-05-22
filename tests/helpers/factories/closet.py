import factory
from factory.django import DjangoModelFactory
from faker import Faker

from .runway import BasicFactory
from chiton.closet.models import Brand, CanonicalSize, Garment, StandardSize

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


def standard_size_factory(canonical_size_factory):
    def create_standard_size(lower_size=None, upper_size=None, is_petite=False, is_plus_sized=False, is_tall=False):
        canonical_kwargs = {'is_plus_sized': is_plus_sized}

        if lower_size is not None:
            canonical_kwargs['range_lower'] = lower_size
        if upper_size is not None or lower_size is not None:
            canonical_kwargs['range_upper'] = upper_size or lower_size

        return StandardSize.objects.create(
            canonical=canonical_size_factory(**canonical_kwargs),
            is_petite=is_petite,
            is_tall=is_tall
        )

    return create_standard_size
