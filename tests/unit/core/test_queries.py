import pytest

from chiton.closet.models import Brand, Color
from chiton.core.queries import cache_query, prime_cached_queries, unbind_signal_handlers


@pytest.mark.django_db
class TestQueryCaching:

    def teardown_method(self, method):
        unbind_signal_handlers()


class TestCacheQuery(TestQueryCaching):

    def test_returns_query(self, color_factory):
        """It returns the wrapped function's query."""
        @cache_query(Color)
        def count_colors():
            return Color.objects.count()

        color_factory()
        assert count_colors() == 1

    def test_caches_query(self, color_factory):
        """It only evaluates the query once."""
        call_count = 0

        @cache_query(Color)
        def count_colors():
            nonlocal call_count
            call_count += 1

            if call_count < 2:
                return Color.objects.count()
            else:
                return 0

        color_factory()
        assert count_colors() == 1
        assert count_colors() == 1

    def test_caches_query_duplicate_names(self, brand_factory, color_factory):
        """It uses separate cache locations for functions with identical names."""
        def make_cached_model_counter(model_class):
            @cache_query(model_class)
            def counter():
                return model_class.objects.count()

            return counter

        count_brands = make_cached_model_counter(Brand)
        count_colors = make_cached_model_counter(Color)

        color_factory()
        assert count_brands() == 0
        assert count_colors() == 1

    def test_caches_query_isolated(self, color_factory):
        """It uses separate cache locations for each cached query."""
        @cache_query(Color)
        def count_colors():
            return Color.objects.count()

        @cache_query(Color)
        def get_all_colors():
            return Color.objects.all()

        color_factory()
        assert count_colors() == 1
        assert get_all_colors().count() == 1
        assert count_colors() == 1
        assert get_all_colors().count() == 1

    def test_refresh_create(self, color_factory):
        """It refreshes the query whenever a related model is created."""
        @cache_query(Color)
        def count_colors():
            return Color.objects.count()

        color_factory()
        assert count_colors() == 1

        color_factory()
        assert count_colors() == 2

    def test_refresh_update(self, color_factory):
        """It refreshes the query whenever a related model is updated."""
        @cache_query(Color)
        def get_color_names():
            return list(Color.objects.values_list('name', flat=True))

        color = color_factory(name='Blue')
        assert get_color_names() == ['Blue']

        color.name = 'Black'
        color.save()
        assert get_color_names() == ['Black']

    def test_refresh_delete(self, color_factory):
        """It refreshes the query whenever a related model is deleted."""
        @cache_query(Color)
        def count_colors():
            return Color.objects.count()

        color = color_factory()
        assert count_colors() == 1

        color.delete()
        assert count_colors() == 0

    def test_refresh_multiple_models(self, brand_factory, color_factory):
        """It refreshes the query whenever any related model is modified."""
        @cache_query(Brand, Color)
        def counts():
            return (Brand.objects.count(), Color.objects.count())

        color_factory()
        assert counts() == (0, 1)
        assert counts() == (0, 1)

        brand_factory()
        assert counts() == (1, 1)

        color_factory()
        assert counts() == (1, 2)


class TestPrimeCachedQueries(TestQueryCaching):

    def test_prime(self):
        """It primes the cache for all known queries."""
        call_count = 0

        @cache_query(Color)
        def count_calls():
            nonlocal call_count
            call_count += 1
            return call_count

        assert call_count == 0
        prime_cached_queries()
        assert call_count == 1


class TestUnbindSignalHandlers(TestQueryCaching):

    def test_unbinds_handlers(self, color_factory):
        """It unbinds all model-change handlers."""
        @cache_query(Color)
        def count_colors():
            return Color.objects.count()

        color_factory()
        assert count_colors() == 1

        unbind_signal_handlers()

        color_factory()
        assert count_colors() == 1
