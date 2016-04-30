from chiton.wintour.pipelines.core import CorePipeline


def make_recommendations(profile, pipeline_class=CorePipeline, serialize=False):
    """Return garment recommendations for a wardrobe profile.

    Args:
        profile (chiton.wintour.models.WardrobeProfile): A wardrobe profile

    Keyword Args:
        pipeline (chiton.wintour.pipelines.BasePipeline): The pipeline to use
        serialize (bool): Whether the dict should be serializable

    Returns:
        dict: The recommendations
    """
    pipeline = pipeline_class()
    recs = pipeline.make_recommendations(profile)

    if not serialize:
        return recs

    serialized = {}
    for basic, values in recs.items():
        value = {
            'facets': {},
            'garments': _serialize_garments(values['garments'])
        }

        for facet, garments in values['facets'].items():
            value['facets'][facet.slug] = _serialize_garments(garments)

        serialized[basic.slug] = value

    return serialized


def _serialize_garments(garments):
    """Serialize a list of Garment models.

    Args:
        garments (list): One or more Garment model instances

    Returns:
        list: The serialized garments
    """
    return []
