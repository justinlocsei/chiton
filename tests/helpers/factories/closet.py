import factory
from factory.django import DjangoModelFactory
from faker import Faker

from .runway import BasicFactory
from chiton.closet.models import Brand, CanonicalSize, Color, Garment, StandardSize

fake = Faker()


class BrandFactory(DjangoModelFactory):

    name = factory.LazyAttribute(lambda m: fake.company())
    age_lower = 20
    age_upper = 40

    class Meta:
        model = Brand


class CanonicalSizeFactory(DjangoModelFactory):

    name = factory.Sequence(lambda n: '%s-%d' % (fake.word(), n))
    range_lower = factory.Sequence(lambda n: n)
    range_upper = factory.Sequence(lambda n: n)

    class Meta:
        model = CanonicalSize


class ColorFactory(DjangoModelFactory):

    name = factory.LazyAttribute(lambda m: fake.company())

    class Meta:
        model = Color


class GarmentFactory(DjangoModelFactory):

    name = factory.LazyAttribute(lambda m: fake.sentence())
    brand = factory.SubFactory(BrandFactory)
    basic = factory.SubFactory(BasicFactory)

    class Meta:
        model = Garment

    @factory.post_generation
    def formalities(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for formality in extracted:
                self.formalities.add(formality)

    @factory.post_generation
    def styles(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for style in extracted:
                self.styles.add(style)


class StandardSizeFactory(DjangoModelFactory):

    canonical = factory.SubFactory(CanonicalSizeFactory)

    class Meta:
        model = StandardSize


def standard_size_factory(canonical_size_factory):
    def create_standard_size(lower_size=None, upper_size=None, is_petite=False, is_plus_sized=False, is_tall=False, is_regular=None, slug=None, canonical=None):
        if not canonical:
            canonical_kwargs = {}
            if lower_size is not None:
                canonical_kwargs['range_lower'] = lower_size
            if upper_size is not None or lower_size is not None:
                canonical_kwargs['range_upper'] = upper_size or lower_size
            if slug:
                canonical_kwargs['slug'] = slug

            canonical = canonical_size_factory(**canonical_kwargs)

        if is_regular is None:
            is_regular = not any([is_petite, is_plus_sized, is_tall])

        return StandardSize.objects.create(
            canonical=canonical,
            is_petite=is_petite,
            is_plus_sized=is_plus_sized,
            is_regular=is_regular,
            is_tall=is_tall
        )

    return create_standard_size
