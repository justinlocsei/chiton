from timeit import default_timer

from django.db import connection

from chiton.closet.models import StandardSize
from chiton.core.queries import cache_query
from chiton.runway.models import Formality, Style
from chiton.wintour.models import WardrobeProfile


def make_recommendations(pipeline_profile, pipeline, debug=False, max_garments_per_group=None):
    """Return garment recommendations for a wardrobe profile.

    Args:
        pipeline_profile (chiton.wintour.profiles.PipelineProfile): A profile for which to make recommendations
        pipeline (chiton.wintour.pipelines.BasePipeline): An instance of a pipeline class

    Keyword Args:
        debug (bool): Whether to generate debug statistics
        max_garments_per_group (int): The maximum number of garments to return per facet group

    Returns:
        chiton.wintour.pipeline.Recommendations: The recommendations data
    """
    if debug:
        previous_queries = set([q['sql'] for q in connection.queries])
        start_time = default_timer()

    recs = pipeline.make_recommendations(pipeline_profile, debug=debug, max_garments_per_group=max_garments_per_group)

    if debug:
        elapsed_time = default_timer() - start_time
        recs['debug'] = {
            'queries': [q for q in connection.queries if q['sql'] not in previous_queries],
            'time': elapsed_time
        }

    return recs


def convert_recommendation_to_wardrobe_profile(recommendation, person=None):
    """Convert a recommendation to a wardrobe profile.

    Args:
        recommendation (chiton.wintour.models.Recommendation): A recommendation

    Keyword Args:
        person (chiton.wintour.models.Person): A person to associate with the profile

    Returns:
        chiton.wintour.models.WardrobeProfile: The created profile
    """
    data = recommendation.profile

    formality_lookup = _get_formality_pks_by_slug()
    size_lookup = _get_size_pks_by_slug()
    style_lookup = _get_style_pks_by_slug()

    profile = WardrobeProfile.objects.create(
        body_shape=data['body_shape'],
        birth_year=data['birth_year'],
        person=person
    )

    profile.styles = [style_lookup[slug] for slug in data['styles']]
    profile.sizes = [size_lookup[slug] for slug in data['sizes']]

    for care_type in data.get('avoid_care', []):
        profile.unwanted_care_types.create(care=care_type)

    for expectation in data['expectations']:
        profile.expectations.create(
            formality_id=formality_lookup[expectation['formality']],
            frequency=expectation['frequency']
        )

    return profile


@cache_query(Formality)
def _get_formality_pks_by_slug():
    """Return a map of slugs to Formality primary keys."""
    by_slug = {}

    for formality in Formality.objects.all().values_list('pk', 'slug'):
        by_slug[formality[1]] = formality[0]

    return by_slug


@cache_query(StandardSize)
def _get_size_pks_by_slug():
    """Return a map of slugs to StandardSize primary keys."""
    by_slug = {}

    for style in StandardSize.objects.all().values_list('pk', 'slug'):
        by_slug[style[1]] = style[0]

    return by_slug


@cache_query(Style)
def _get_style_pks_by_slug():
    """Return a map of slugs to Style primary keys."""
    by_slug = {}

    for style in Style.objects.all().values_list('pk', 'slug'):
        by_slug[style[1]] = style[0]

    return by_slug
