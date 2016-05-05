from chiton.wintour.pipeline import PipelineProfile
from chiton.wintour.pipelines.core import CorePipeline


def make_recommendations(pipeline_profile, pipeline_class=CorePipeline, debug=False):
    """Return garment recommendations for a wardrobe profile.

    Args:
        pipeline_profile (chiton.wintour.pipeline.PipelineProfile): A profile for which to make recommendations

    Keyword Args:
        pipeline (chiton.wintour.pipelines.BasePipeline): The pipeline to use
        debug (bool): Whether to generate debug statistics

    Returns:
        dict: The recommendations
    """
    pipeline = pipeline_class()
    return pipeline.make_recommendations(pipeline_profile, debug=debug)


def package_wardrobe_profile(profile):
    """Convert a wardrobe profile into a pipeline profile.

    Args:
        profile (chiton.wintour.models.WardrobeProfile): A wardrobe profile

    Returns:
        chiton.wintour.pipeline.PipelineProfile: The packaged profile
    """
    data = {
        'age': profile.age,
        'body_shape': profile.shape
    }

    data['styles'] = [style.slug for style in profile.styles.all()]

    expectations = {}
    for expectation in profile.expectations.all().select_related('formality'):
        expectations[expectation.formality.slug] = expectation.frequency
    data['expectations'] = expectations

    return PipelineProfile(**data)


def serialize_recommendations(recommendations):
    """Serialize generated recommendations as a primitive-only dictionary.

    Args:
        recommendations (dict): A dict of recommendations with model instances

    Returns:
        dict: The recommenations as a dict of primitives
    """
    serialized = {}
    for basic, values in recommendations.items():
        value = {
            'basic': {
                'name': basic.name,
                'pk': basic.pk,
                'slug': basic.slug
            },
            'facets': {},
            'garments': _serialize_weighted_garments(values['garments'])
        }

        for facet, garments in values['facets'].items():
            value['facets'][facet.slug] = _serialize_weighted_garments(garments)

        serialized[basic.slug] = value

    return serialized


def _serialize_weighted_garments(garments):
    """Serialize a list of weighted garments.

    Args:
        garments (list): One or more dicts describing a garment and a weight

    Returns:
        list: The serialized weighted garments
    """
    return [_serialize_weighted_garment(garment) for garment in garments]


def _serialize_weighted_garment(weighted):
    """Serialize a single weighted garment.

    Args:
        weighted (dict): A dictionary describing the garment and its weight

    Returns:
        dict: A primitive representation of the garment and its weight
    """
    garment = weighted['garment']

    garment_dict = {
        'name': garment.name,
        'slug': garment.slug,
        'brand': garment.brand.name,
        'pk': garment.pk
    }

    return {
        'explanations': weighted['explanations'],
        'garment': garment_dict,
        'urls': weighted['urls'],
        'weight': weighted['weight']
    }
