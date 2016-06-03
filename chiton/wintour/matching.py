from timeit import default_timer

from django.db import connection

from chiton.wintour.pipeline import PipelineProfile


# Field names for serializing garments
GARMENT_IMAGE_FIELDS = ('image', 'thumbnail')
GARMENT_IMAGE_ATTRIBUTES = ('height', 'url', 'width')


def package_wardrobe_profile(profile):
    """Convert a wardrobe profile into a pipeline profile.

    Args:
        profile (chiton.wintour.models.WardrobeProfile): A wardrobe profile

    Returns:
        chiton.wintour.pipeline.PipelineProfile: The packaged profile
    """
    data = {
        'age': profile.age,
        'avoid_care': [c.care for c in profile.unwanted_care_types.all()],
        'body_shape': profile.body_shape,
        'sizes': [size.slug for size in profile.sizes.all()],
        'styles': [style.slug for style in profile.styles.all()]
    }

    expectations = {}
    for expectation in profile.expectations.all().select_related('formality'):
        expectations[expectation.formality.slug] = expectation.frequency
    data['expectations'] = expectations

    return PipelineProfile(data)


def make_recommendations(pipeline_profile, pipeline, debug=False):
    """Return garment recommendations for a wardrobe profile.

    Args:
        pipeline_profile (chiton.wintour.pipeline.PipelineProfile): A profile for which to make recommendations

    Keyword Args:
        pipeline (chiton.wintour.pipelines.BasePipeline): An instance of a pipeline class
        debug (bool): Whether to generate debug statistics

    Returns:
        dict: The recommendations data
    """
    if debug:
        previous_queries = set([q['sql'] for q in connection.queries])
        start_time = default_timer()

    recs = Recommendations({
        'basics': pipeline.make_recommendations(pipeline_profile, debug=debug)
    })

    if debug:
        elapsed_time = default_timer() - start_time
        recs['debug'] = {
            'queries': [q for q in connection.queries if q['sql'] not in previous_queries],
            'time': elapsed_time
        }

    return recs


def serialize_recommendations(recommendations):
    """Serialize generated recommendations as a primitive-only dictionary.

    Args:
        recommendations (dict): A dict of recommendations with model instances

    Returns:
        dict: The recommendations as a dict of primitives
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

        for facet, groups in values['facets'].items():
            value['facets'][facet.slug] = groups

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
            if not image_obj:
                continue

            image_dict = {}
            for image_attribute in GARMENT_IMAGE_ATTRIBUTES:
                image_dict[image_attribute] = getattr(image_obj, image_attribute)
            item_dict[image_field] = image_dict

        item_dict.update({
            'id': item.pk,
            'price': int(float(item.price) * 100) if item.price else None,
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
