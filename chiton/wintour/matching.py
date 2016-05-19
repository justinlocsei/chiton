from timeit import default_timer

from django.db import connection

from chiton.wintour.pipeline import PipelineProfile
from chiton.wintour.pipelines.core import CorePipeline


# Field names for serializing garments
GARMENT_IMAGE_FIELDS = ('image', 'thumbnail')
GARMENT_IMAGE_ATTRIBUTES = ('height', 'url', 'width')


def make_recommendations(pipeline_profile, pipeline_class=CorePipeline, debug=False):
    """Return garment recommendations for a wardrobe profile.

    Args:
        pipeline_profile (chiton.wintour.pipeline.PipelineProfile): A profile for which to make recommendations

    Keyword Args:
        pipeline (chiton.wintour.pipelines.BasePipeline): The pipeline to use
        debug (bool): Whether to generate debug statistics

    Returns:
        dict: The recommendations data
    """
    if debug:
        previous_queries = set([q['sql'] for q in connection.queries])
        start_time = default_timer()

    pipeline = pipeline_class()
    recs = {'basics': pipeline.make_recommendations(pipeline_profile, debug=debug)}

    if debug:
        elapsed_time = default_timer() - start_time
        recs['debug'] = {
            'queries': [q for q in connection.queries if q['sql'] not in previous_queries],
            'time': elapsed_time
        }

    return recs


def package_wardrobe_profile(profile):
    """Convert a wardrobe profile into a pipeline profile.

    Args:
        profile (chiton.wintour.models.WardrobeProfile): A wardrobe profile

    Returns:
        chiton.wintour.pipeline.PipelineProfile: The packaged profile
    """
    data = {
        'age': profile.age,
        'body_shape': profile.body_shape,
        'styles': [style.slug for style in profile.styles.all()]
    }

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
    basics = {}

    for basic, values in recommendations['basics'].items():
        value = {
            'basic': {
                'id': basic.pk,
                'name': basic.name,
                'slug': basic.slug
            },
            'facets': {},
            'garments': _serialize_weighted_garments(values['garments'])
        }

        for facet, garments in values['facets'].items():
            value['facets'][facet.slug] = _serialize_weighted_garments(garments)

        basics[basic.slug] = value

    serialized = {'basics': basics}
    if 'debug' in recommendations:
        serialized['debug'] = recommendations['debug']

    return serialized


def _serialize_weighted_garments(garments):
    """Serialize a list of weighted garments.

    Args:
        garments (list): One or more dicts describing a weighted garment

    Returns:
        list: The serialized weighted garments
    """
    return [_serialize_weighted_garment(garment) for garment in garments]


def _serialize_weighted_garment(weighted):
    """Serialize a single weighted garment.

    Args:
        weighted (dict): A dictionary describing the weighted garment

    Returns:
        dict: A primitive-only representation of the garment and its weight
    """
    garment = weighted['garment']

    garment_dict = {
        'brand': garment.brand.name,
        'id': garment.pk,
        'name': garment.name,
        'slug': garment.slug
    }

    items_list = []
    for item in weighted['affiliate_items']:

        item_dict = {}
        for image_field in GARMENT_IMAGE_FIELDS:
            image_obj = getattr(item, image_field)

            image_dict = {}
            for image_attribute in GARMENT_IMAGE_ATTRIBUTES:
                image_dict[image_attribute] = getattr(image_obj, image_attribute)
            item_dict[image_field] = image_dict

        item_dict.update({
            'id': item.pk,
            'price': int(float(item.price) * 100),
            'network_name': item.network.name,
            'network_id': item.network.pk,
            'url': item.url
        })
        items_list.append(item_dict)

    return {
        'affiliate_items': items_list,
        'explanations': weighted['explanations'],
        'garment': garment_dict,
        'weight': weighted['weight']
    }
