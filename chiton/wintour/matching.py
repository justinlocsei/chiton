from timeit import default_timer

from django.db import connection

from chiton.wintour.pipeline import PipelineProfile


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


def make_recommendations(pipeline_profile, pipeline, debug=False):
    """Return garment recommendations for a wardrobe profile.

    Args:
        pipeline_profile (chiton.wintour.pipeline.PipelineProfile): A profile for which to make recommendations

    Keyword Args:
        pipeline (chiton.wintour.pipelines.BasePipeline): An instance of a pipeline class
        debug (bool): Whether to generate debug statistics

    Returns:
        chiton.wintour.pipeline.Recommendations: The recommendations data
    """
    if debug:
        previous_queries = set([q['sql'] for q in connection.queries])
        start_time = default_timer()

    recs = pipeline.make_recommendations(pipeline_profile, debug=debug)

    if debug:
        elapsed_time = default_timer() - start_time
        recs['debug'] = {
            'queries': [q for q in connection.queries if q['sql'] not in previous_queries],
            'time': elapsed_time
        }

    return recs
