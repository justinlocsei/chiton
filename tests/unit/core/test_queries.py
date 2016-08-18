import pytest

from chiton.closet.models import Brand, Color, Garment
from chiton.core.queries import bind_signal_handlers, cache_query, prime_cached_queries, unbind_signal_handlers


NAMESPACE = 'test_queries'
NAMESPACE_TWO = 'test_queries_2'


@pytest.mark.django_db
class TestQueryCaching:

    def teardown_method(self, method):
        unbind_signal_handlers(NAMESPACE)
        unbind_signal_handlers(NAMESPACE_TWO)


class TestCacheQuery(TestQueryCaching):

    def test_returns_query(self, color_factory):
        """It returns the wrapped function's query."""
        @cache_query(Color, namespace=NAMESPACE)
        def count_colors():
            return Color.objects.count()

        color_factory()
        assert count_colors() == 1

    def test_caches_query(self, color_factory):
        """It only evaluates the query once."""
        call_count = 0

        @cache_query(Color, namespace=NAMESPACE)
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
            @cache_query(model_class, namespace=NAMESPACE)
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
        @cache_query(Color, namespace=NAMESPACE)
        def count_colors():
            return Color.objects.count()

        @cache_query(Color, namespace=NAMESPACE)
        def get_all_colors():
            return Color.objects.all()

        color_factory()
        assert count_colors() == 1
        assert get_all_colors().count() == 1
        assert count_colors() == 1
        assert get_all_colors().count() == 1

    def test_refresh_create(self, color_factory):
        """It refreshes the query whenever a related model is created."""
        @cache_query(Color, namespace=NAMESPACE)
        def count_colors():
            return Color.objects.count()

        bind_signal_handlers(NAMESPACE)

        color_factory()
        assert count_colors() == 1

        color_factory()
        assert count_colors() == 2

    def test_refresh_update(self, color_factory):
        """It refreshes the query whenever a related model is updated."""
        @cache_query(Color, namespace=NAMESPACE)
        def get_color_names():
            return list(Color.objects.values_list('name', flat=True))

        bind_signal_handlers(NAMESPACE)

        color = color_factory(name='Blue')
        assert get_color_names() == ['Blue']

        color.name = 'Black'
        color.save()
        assert get_color_names() == ['Black']

    def test_refresh_delete(self, color_factory):
        """It refreshes the query whenever a related model is deleted."""
        @cache_query(Color, namespace=NAMESPACE)
        def count_colors():
            return Color.objects.count()

        bind_signal_handlers(NAMESPACE)

        color = color_factory()
        assert count_colors() == 1

        color.delete()
        assert count_colors() == 0

    def test_refresh_multiple_models(self, brand_factory, color_factory):
        """It refreshes the query whenever any related model is modified."""
        @cache_query(Brand, Color, namespace=NAMESPACE)
        def counts():
            return (Brand.objects.count(), Color.objects.count())

        bind_signal_handlers(NAMESPACE)

        color_factory()
        assert counts() == (0, 1)
        assert counts() == (0, 1)

        brand_factory()
        assert counts() == (1, 1)

        color_factory()
        assert counts() == (1, 2)

    def test_refresh_m2m_updated(self, garment_factory, formality_factory):
        """It refreshes the query whenever a many-to-many model is updated."""
        @cache_query(Garment, namespace=NAMESPACE)
        def count():
            garments = Garment.objects.all().order_by('pk')
            if garments.count():
                return garments[0].formalities.count()
            else:
                return 0

        bind_signal_handlers(NAMESPACE)

        casual = formality_factory()
        executive = formality_factory()

        garment = garment_factory()
        assert count() == 0

        garment.formalities.add(casual)
        assert count() == 1

        garment.formalities.add(executive)
        assert count() == 2

        garment.formalities.remove(executive)
        assert count() == 1


class TestPrimeCachedQueries(TestQueryCaching):

    def test_prime(self):
        """It primes the cache for all known queries."""
        call_count = 0

        @cache_query(Color, namespace=NAMESPACE)
        def count_calls():
            nonlocal call_count
            call_count += 1
            return call_count

        bind_signal_handlers(NAMESPACE)

        assert call_count == 0
        prime_cached_queries()
        assert call_count == 1


class TestBindSignalHandlers(TestQueryCaching):

    def test_binds_handlers(self, color_factory):
        """It binds all model-change handlers."""
        @cache_query(Color, namespace=NAMESPACE)
        def count_colors():
            return Color.objects.count()

        color_factory()
        assert count_colors() == 1

        color_factory()
        assert count_colors() == 1

        bind_signal_handlers(NAMESPACE)
        assert count_colors() == 1

        color_factory()
        assert count_colors() == 3

    def test_namespace(self, color_factory):
        """It can selectively bind namespaced queries."""
        @cache_query(Color, namespace=NAMESPACE)
        def count_colors():
            return Color.objects.count()

        @cache_query(Color, namespace=NAMESPACE_TWO)
        def double_colors():
            return Color.objects.count() * 2

        assert count_colors() == 0
        assert double_colors() == 0

        color_factory()
        assert count_colors() == 0
        assert double_colors() == 0

        bind_signal_handlers(NAMESPACE)

        color_factory()
        assert count_colors() == 2
        assert double_colors() == 0

        bind_signal_handlers(NAMESPACE_TWO)

        color_factory()
        assert count_colors() == 3
        assert double_colors() == 6

    def test_binds_idempotent(self, color_factory):
        """It can accept multiple bind calls."""
        @cache_query(Color, namespace=NAMESPACE)
        def count_colors():
            return Color.objects.count()

        color_factory()
        assert count_colors() == 1

        bind_signal_handlers(NAMESPACE)
        bind_signal_handlers(NAMESPACE)

        color_factory()
        assert count_colors() == 2


class TestUnbindSignalHandlers(TestQueryCaching):

    def test_unbinds_handlers(self, color_factory):
        """It unbinds all model-change handlers."""
        @cache_query(Color, namespace=NAMESPACE)
        def count_colors():
            return Color.objects.count()

        color_factory()
        assert count_colors() == 1

        unbind_signal_handlers(NAMESPACE)

        color_factory()
        assert count_colors() == 1

    def test_namespace(self, color_factory):
        """It can selectively unbind namespaced queries."""
        @cache_query(Color, namespace=NAMESPACE)
        def count_colors():
            return Color.objects.count()

        @cache_query(Color, namespace=NAMESPACE_TWO)
        def double_colors():
            return Color.objects.count() * 2

        bind_signal_handlers(NAMESPACE)
        bind_signal_handlers(NAMESPACE_TWO)

        assert count_colors() == 0
        assert double_colors() == 0

        color_factory()
        assert count_colors() == 1
        assert double_colors() == 2

        unbind_signal_handlers(NAMESPACE)

        color_factory()
        assert count_colors() == 1
        assert double_colors() == 4

        unbind_signal_handlers(NAMESPACE_TWO)

        color_factory()
        assert count_colors() == 1
        assert double_colors() == 4

    def test_unbinds_idempotent(self, color_factory):
        """It can accept multiple unbind calls."""
        @cache_query(Color, namespace=NAMESPACE)
        def count_colors():
            return Color.objects.count()

        color_factory()
        assert count_colors() == 1

        unbind_signal_handlers(NAMESPACE)
        unbind_signal_handlers(NAMESPACE)

        color_factory()
        assert count_colors() == 1
