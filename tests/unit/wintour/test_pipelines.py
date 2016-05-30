import pytest

from chiton.closet.models import Garment
from chiton.wintour.facets import BaseFacet
from chiton.wintour.garment_filters import BaseGarmentFilter
from chiton.wintour.pipeline import PipelineStep
from chiton.wintour.pipelines import BasePipeline
from chiton.wintour.query_filters import BaseQueryFilter
from chiton.wintour.weights import BaseWeight


@pytest.mark.django_db
class TestBasePipeline:

    def test_provide_garments(self, garment_factory):
        """It provides the full queryset of garments."""
        garment_factory()
        garment_factory()

        garments = BasePipeline().provide_garments()

        assert garments.count() == 2

    def test_load_garments(self, garment_factory):
        """It allows each pipeline step to modify the garment queryset."""
        for i in range(0, 5):
            garment_factory()

        def slice_garments(garments):
            return garments[:garments.count() - 1]

        class TestQueryFilter(BaseQueryFilter):
            name = 'Test Query Filter'
            slug = 'test-query-filter'

            def prepare_garments(self, garments):
                return slice_garments(garments)

        class TestGarmentFilter(BaseGarmentFilter):
            name = 'Test Garment Filter'
            slug = 'test-garment-filter'

            def prepare_garments(self, garments):
                return slice_garments(garments)

        class TestWeight(BaseWeight):
            name = 'Test Weight'
            slug = 'test-weight'

            def prepare_garments(self, garments):
                return slice_garments(garments)

        class TestFacet(BaseFacet):
            name = 'Test Facet'
            slug = 'test-face'

            def prepare_garments(self, garments):
                return slice_garments(garments)

        class TestPipeline(BasePipeline):

            def provide_query_filters(self):
                return [TestQueryFilter()]

            def provide_garment_filters(self):
                return [TestGarmentFilter()]

            def provide_weights(self):
                return [TestWeight()]

            def provide_facets(self):
                return [TestFacet()]

        garments = TestPipeline().load_garments()
        assert garments.count() == 1
