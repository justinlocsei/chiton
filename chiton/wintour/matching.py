from timeit import default_timer

from django.db import connection


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
