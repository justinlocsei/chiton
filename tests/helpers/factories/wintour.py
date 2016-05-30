from faker import Faker

from chiton.wintour.data import BODY_SHAPES
from chiton.wintour.models import WardrobeProfile

fake = Faker()


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
