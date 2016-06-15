import pytest

from chiton.closet.models import Garment
from chiton.runway.data import PROPRIETY_IMPORTANCES
from chiton.runway.models import Propriety
from chiton.wintour.data import EXPECTATION_FREQUENCIES
from chiton.wintour.query_filters.formality import FormalityQueryFilter


@pytest.mark.django_db
class TestFormalityQueryFilter:

    def test_apply_default(self, garment_factory, pipeline_profile_factory):
        """It returns an unfiltered garment queryset by default."""
        garment_factory()
        garment_factory()
        query = Garment.objects.all()

        query_filter = FormalityQueryFilter()
        profile = pipeline_profile_factory()

        with query_filter.apply_to_profile(profile) as filter_fn:
            result = filter_fn(query)

        assert query.count() == 2
        assert result.count() == 2

    def test_apply_exclusion(self, basic_factory, formality_factory, garment_factory, pipeline_profile_factory):
        """It excludes garments whose basic type is inappropriate for the user's formality."""
        casual = formality_factory(slug='casual')
        executive = formality_factory(slug='executive')

        jeans_basic = basic_factory()
        blazer_basic = basic_factory()
        dress_basic = basic_factory()

        jeans = garment_factory(basic=jeans_basic)
        blazer = garment_factory(basic=blazer_basic)
        dress = garment_factory(basic=dress_basic)
        query = Garment.objects.all()

        Propriety.objects.create(basic=jeans_basic, formality=casual, importance=PROPRIETY_IMPORTANCES['ALWAYS'])
        Propriety.objects.create(basic=jeans_basic, formality=executive, importance=PROPRIETY_IMPORTANCES['NOT'])
        Propriety.objects.create(basic=blazer_basic, formality=executive, importance=PROPRIETY_IMPORTANCES['ALWAYS'])
        Propriety.objects.create(basic=blazer_basic, formality=casual, importance=PROPRIETY_IMPORTANCES['NOT'])
        Propriety.objects.create(basic=dress_basic, formality=executive, importance=PROPRIETY_IMPORTANCES['MILDLY'])
        Propriety.objects.create(basic=dress_basic, formality=casual, importance=PROPRIETY_IMPORTANCES['MILDLY'])

        casual_profile = pipeline_profile_factory(expectations=[
            {'formality': 'casual', 'frequency': EXPECTATION_FREQUENCIES['ALWAYS']},
            {'formality': 'executive', 'frequency': EXPECTATION_FREQUENCIES['NEVER']}
        ])
        executive_profile = pipeline_profile_factory(expectations=[
            {'formality': 'casual', 'frequency': EXPECTATION_FREQUENCIES['NEVER']},
            {'formality': 'executive', 'frequency': EXPECTATION_FREQUENCIES['ALWAYS']}
        ])
        mixed_profile = pipeline_profile_factory(expectations=[
            {'formality': 'casual', 'frequency': EXPECTATION_FREQUENCIES['SOMETIMES']},
            {'formality': 'executive', 'frequency': EXPECTATION_FREQUENCIES['SOMETIMES']}
        ])

        query_filter = FormalityQueryFilter()

        with query_filter.apply_to_profile(casual_profile) as filter_fn:
            casual_result = filter_fn(query)

        with query_filter.apply_to_profile(executive_profile) as filter_fn:
            executive_result = filter_fn(query)

        with query_filter.apply_to_profile(mixed_profile) as filter_fn:
            mixed_result = filter_fn(query)

        assert query.count() == 3

        assert casual_result.count() == 2
        assert jeans in casual_result
        assert dress in casual_result
        assert blazer not in casual_result

        assert executive_result.count() == 2
        assert blazer in executive_result
        assert dress in executive_result
        assert jeans not in executive_result

        assert mixed_result.count() == 2
        assert blazer in mixed_result
        assert jeans in mixed_result
        assert dress not in mixed_result
