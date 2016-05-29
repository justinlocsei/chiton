from chiton.wintour.pipelines.core import CorePipeline


class TestCorePipeline:

    def test_query_filters(self):
        """It provides a list of query filters."""
        query_filters = CorePipeline().provide_query_filters()
        assert query_filters

    def test_garment_filters(self):
        """It provides a list of garment filters."""
        garment_filters = CorePipeline().provide_garment_filters()
        assert garment_filters

    def test_weights(self):
        """It provides a list of non-uniform weights."""
        weights = CorePipeline().provide_weights()
        importances = set([w.importance for w in weights])

        assert len(weights) > 1
        assert len(importances) > 1

    def test_facets(self):
        """It provides a list of garment filters."""
        facets = CorePipeline().provide_facets()
        assert facets
