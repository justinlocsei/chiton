from django.core.cache import cache


def isolate_cache_tests(request):
    """Ensure that each test starts and ends with an empty cache."""
    cache.clear()
    request.addfinalizer(cache.clear)
