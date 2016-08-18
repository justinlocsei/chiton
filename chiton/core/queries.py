from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save


# A list of all cached queries
CACHED_QUERIES = []

# All model signals that should trigger a cache refresh
MODEL_SIGNALS = (post_delete, post_save)

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

        # Wrap the query in a get-or-set cache call
        def run_query():
            result = cache.get(query_guid)
            if result is None:
                result = query_fn()
                cache.set(query_guid, result, None)

            return result

        # Define a signal handler that refreshes the cached value
        def refresh_query(*args, **kwargs):
            cache.delete(query_guid)
            cache.set(query_guid, query_fn(), None)

        # Add the query to the master list
        CACHED_QUERIES.append({
            'guid': query_guid,
            'id': query_id,
            'model_classes': model_classes,
            'refresh_fn': refresh_query
        })

        return run_query

    return wrap_query


def bind_signal_handlers(namespace=''):
    """Register the signal handlers for all query models.

    Keyword Args:
        namespace (str): The namespace for which to register handlers
    """
    namespace_prefix = namespace
    if namespace_prefix:
        namespace_prefix = '%s%s' % (namespace, NAMESPACE_SEPARATOR)

    for query in CACHED_QUERIES:
        if query['guid'].startswith(namespace_prefix):
            for model_class in query['model_classes']:

                # Bind model signals on the model itself
                for signal in MODEL_SIGNALS:
                    signal.connect(query['refresh_fn'], sender=model_class, dispatch_uid=query['guid'])

                # Bind M2M-changed signals on the model's M2M fields
                for field in model_class._meta.get_fields():
                    related = getattr(field, 'remote_field')
                    if getattr(field, 'many_to_many', False) and hasattr(related, 'through'):
                        m2m_changed.connect(query['refresh_fn'], sender=field.remote_field.through, dispatch_uid=query['guid'])


def prime_cached_queries():
    """Prime all cached queries."""
    for query in CACHED_QUERIES:
        query['refresh_fn']()


def unbind_signal_handlers(namespace=''):
    """Unbind all connected signal handlers.

    Keyword Args:
        namespace (str): The namespace for which to unbind queries
    """
    namespace_prefix = namespace
    if namespace_prefix:
        namespace_prefix = '%s%s' % (namespace, NAMESPACE_SEPARATOR)

    for query in CACHED_QUERIES:
        for model_class in query['model_classes']:
            for signal in MODEL_SIGNALS:
                if query['guid'].startswith(namespace_prefix):
                    signal.disconnect(None, sender=model_class, dispatch_uid=query['guid'])
