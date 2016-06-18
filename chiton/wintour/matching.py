from timeit import default_timer

from django.db import connection


def make_recommendations(pipeline_profile, pipeline, debug=False):
    """Return garment recommendations for a wardrobe profile.

    Args:
        pipeline_profile (chiton.wintour.profiles.PipelineProfile): A profile for which to make recommendations

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
