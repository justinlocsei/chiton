from datetime import datetime
import factory
from factory.django import DjangoModelFactory
from faker import Faker

from chiton.closet.data import CARE_TYPES
from chiton.wintour.data import BODY_SHAPES, EXPECTATION_FREQUENCIES
from chiton.wintour.models import Person, Recommendation, WardrobeProfile
from chiton.wintour.profiles import PipelineProfile


fake = Faker()


def get_default_birth_year():
    return datetime.now().year


def pipeline_profile_factory(formality_factory, standard_size_factory, style_factory):
    def create_pipeline_profile(avoid_care=None, birth_year=None, body_shape=BODY_SHAPES['APPLE'], expectations=None, sizes=None, styles=None):
        if not birth_year:
            birth_year = get_default_birth_year()

        if not sizes:
            sizes = [standard_size_factory().slug]

        if not styles:
            styles = [style_factory().slug]

        if not expectations:
            expectations = [{
                'formality': formality_factory().slug,
                'frequency': EXPECTATION_FREQUENCIES['SOMETIMES']
            }]

        data = {
            'avoid_care': [CARE_TYPES['HAND_WASH']] if avoid_care is None else avoid_care,
            'birth_year': birth_year,
            'body_shape': body_shape,
            'expectations': expectations,
            'sizes': sizes,
            'styles': styles
        }

        return PipelineProfile(data)

    return create_pipeline_profile


def wardrobe_profile_factory(standard_size_factory, style_factory):
    def create_wardrobe_profile(birth_year=None, body_shape=BODY_SHAPES['APPLE'], styles=None, sizes=None):
        if birth_year is None:
            birth_year = get_default_birth_year()

        profile = WardrobeProfile.objects.create(body_shape=body_shape, birth_year=birth_year)

        if styles is None:
            styles = [style_factory(), style_factory()]
        for style in styles:
            profile.styles.add(style)

        if sizes is None:
            sizes = [standard_size_factory(), standard_size_factory()]
        for size in sizes:
            profile.sizes.add(size)

        return profile

    return create_wardrobe_profile


class PersonFactory(DjangoModelFactory):

    first_name = factory.LazyAttribute(lambda p: fake.first_name())
    last_name = factory.LazyAttribute(lambda p: fake.last_name())
    email = factory.LazyAttribute(lambda p: fake.email())

    class Meta:
        model = Person


class RecommendationFactory(DjangoModelFactory):

    profile = factory.LazyAttribute(lambda r: wardrobe_profile_factory())

    class Meta:
        model = Recommendation
