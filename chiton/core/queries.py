from django.core.cache import cache
from django.db.models.signals import post_delete, post_save


# A list of all cached queries
CACHED_QUERIES = []

# All model signals that should trigger a cache refresh
REFRESH_SIGNALS = (post_delete, post_save)

# The separator used for namespaces
NAMESPACE_SEPARATOR = ':'


def cache_query(*model_classes, namespace='default'):
    """Cache a function that returns a query's value.

    Args:
        model_class (list[django.db.models.Model]): All model classes involved in the query

    Keyword Args:
        namespace (str): A namespace to use for the caching

    Returns:
        function: The query-producing function with cache logic added
    """
    def wrap_query(query_fn):
        query_id = '%s%scache_query_%s' % (namespace, NAMESPACE_SEPARATOR, query_fn.__name__)
        other_queries = len([q for q in CACHED_QUERIES if q['id'] == query_id])
        query_guid = '%s--%d' % (query_id, other_queries)

        def run_query():
            result = cache.get(query_guid)
            if result is None:
                result = query_fn()
                cache.set(query_guid, result, None)

            return result

        # Register a signal handler that refreshes the cached value when an
        # involved model is changed
        def refresh_query(*args, **kwargs):
            cache.delete(query_guid)
            cache.set(query_guid, query_fn(), None)
        for model_class in model_classes:
            for signal in REFRESH_SIGNALS:
                signal.connect(refresh_query, sender=model_class, dispatch_uid=query_guid)

        # Add the query to the master list
        CACHED_QUERIES.append({
            'guid': query_guid,
            'id': query_id,
            'model_classes': model_classes,
            'refresh_fn': refresh_query
        })

        return run_query

    return wrap_query


def prime_cached_queries():
    """Prime all cached queries."""
    for query in CACHED_QUERIES:
        query['refresh_fn']()


def unbind_signal_handlers(namespace=None):
    """Unbind all connected signal handlers.

    Keyword Args:
        namespace (str): The namespace for which to unbind queries
    """
    if namespace is None:
        namespace_prefix = ''
    else:
        namespace_prefix = '%s%s' % (namespace, NAMESPACE_SEPARATOR)

    for query in CACHED_QUERIES:
        for model_class in query['model_classes']:
            for signal in REFRESH_SIGNALS:
                if query['guid'].startswith(namespace_prefix):
                    signal.disconnect(None, sender=model_class, dispatch_uid=query['guid'])
