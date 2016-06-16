import voluptuous as V

from chiton.closet.data import CARE_TYPES
from chiton.closet.models import StandardSize
from chiton.core.schema import define_data_shape, NumberInRange, OneOf
from chiton.runway.models import Formality, Style
from chiton.wintour.data import BODY_SHAPES, EXPECTATION_FREQUENCIES


PipelineProfile = define_data_shape({
    V.Required('age'): NumberInRange(0, 100),
    V.Required('avoid_care'): list(CARE_TYPES.values()),
    V.Required('body_shape'): OneOf(BODY_SHAPES.values()),
    V.Required('expectations'): [{
        V.Required('formality'): str,
        V.Required('frequency'): OneOf(EXPECTATION_FREQUENCIES.values())
    }],
    V.Required('sizes'): [str],
    V.Required('styles'): [str]
})


def package_wardrobe_profile(profile):
    """Convert a wardrobe profile into a pipeline profile.

    Args:
        profile (chiton.wintour.models.WardrobeProfile): A wardrobe profile

    Returns:
        chiton.wintour.profiles.PipelineProfile: The packaged profile
    """
    data = {
        'age': profile.age,
        'avoid_care': [c.care for c in profile.unwanted_care_types.all()],
        'body_shape': profile.body_shape,
        'expectations': [],
        'sizes': [size.slug for size in profile.sizes.all()],
        'styles': [style.slug for style in profile.styles.all()]
    }

    for expectation in profile.expectations.all().select_related('formality'):
        data['expectations'].append({
            'formality': expectation.formality.slug,
            'frequency': expectation.frequency
        })

    return PipelineProfile(data)
