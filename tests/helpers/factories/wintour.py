from faker import Faker

from chiton.closet.data import CARE_TYPES
from chiton.wintour.data import BODY_SHAPES, EXPECTATION_FREQUENCIES
from chiton.wintour.models import WardrobeProfile
from chiton.wintour.profiles import PipelineProfile


fake = Faker()


def pipeline_profile_factory(formality_factory, standard_size_factory, style_factory):
    def create_pipeline_profile(age=50, avoid_care=None, body_shape=BODY_SHAPES['APPLE'], expectations=None, sizes=None, styles=None):
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
            'age': age,
            'avoid_care': avoid_care or [CARE_TYPES['HAND_WASH']],
            'body_shape': body_shape,
            'expectations': expectations,
            'sizes': sizes,
            'styles': styles
        }

        return PipelineProfile(data)

    return create_pipeline_profile


def wardrobe_profile_factory(standard_size_factory, style_factory):
    def create_wardrobe_profile(body_shape=BODY_SHAPES['APPLE'], age=50, styles=None, sizes=None):
        profile = WardrobeProfile.objects.create(body_shape=body_shape, age=age)

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
