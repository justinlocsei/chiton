import pytest

from chiton.closet.models import Garment
from chiton.wintour.pipeline import PipelineProfile
from chiton.wintour.weights.age import AgeWeight


@pytest.fixture
def garment_40_to_50(brand_factory, garment_factory):
    brand = brand_factory(age_lower=40, age_upper=50)
    return garment_factory(brand=brand)


@pytest.mark.django_db
class TestAgeWeight:

    def test_prepare_garments(self, garment_factory):
        """It processes the garments queryset."""
        garment_factory()
        garment_factory()

        garments = Garment.objects.all()
        prepared = AgeWeight().prepare_garments(garments)

        assert garments.count() == 2
        assert prepared.count() == 2

    def test_outside_range(self, garment_40_to_50):
        """It returns a null weight when a garment's brand's age range is well outside the user's age."""
        profile = PipelineProfile(age=30)
        weight = AgeWeight(tail_years=5)

        with weight.apply_to_profile(profile) as apply_fn:
            result = apply_fn(garment_40_to_50)
            assert not result

    def test_inside_range(self, garment_40_to_50):
        """It applies weight to garments whose brand's age range is inside of or near the user's age."""
        weight = AgeWeight(tail_years=5)

        ages = {
            'out_lower': 34,
            'in_lower_tail_end': 35,
            'in_lower_tail': 39,
            'in_lower': 40,
            'in_middle': 45,
            'in_upper': 50,
            'in_upper_tail': 51,
            'in_upper_tail_end': 55,
            'out_upper': 56
        }

        results = {}
        for label, age in ages.items():
            profile = PipelineProfile(age=age)
            with weight.apply_to_profile(profile) as apply_fn:
                results[label] = apply_fn(garment_40_to_50)

        assert not results['out_lower']
        assert not results['out_upper']

        assert results['in_lower_tail_end'] == results['in_lower_tail']
        assert results['in_upper_tail'] == results['in_upper_tail_end']
        assert results['in_lower_tail'] == results['in_upper_tail']

        assert results['in_lower'] == results['in_middle'] == results['in_upper']
        assert results['in_lower_tail'] < results['in_lower']
        assert results['in_upper_tail'] < results['in_upper']

    def test_inside_range_tail(self, garment_40_to_50):
        """It allows the tail range in years to be configurable."""
        weight_long_tail = AgeWeight(tail_years=10)
        weight_short_tail = AgeWeight(tail_years=1)

        profile = PipelineProfile(age=35)

        with weight_long_tail.apply_to_profile(profile) as apply_fn:
            result_long_tail = apply_fn(garment_40_to_50)

        with weight_short_tail.apply_to_profile(profile) as apply_fn:
            result_short_tail = apply_fn(garment_40_to_50)

        assert not result_short_tail
        assert result_long_tail

    def test_debug(self, brand_factory, garment_factory):
        """It logs explanations for any garments that receive an age weight."""
        young_brand = brand_factory(age_lower=20, age_upper=30)
        mature_brand = brand_factory(age_lower=35, age_upper=40)
        old_brand = brand_factory(age_lower=70, age_upper=80)

        garment_young = garment_factory(brand=young_brand)
        garment_mature = garment_factory(brand=mature_brand)
        garment_old = garment_factory(brand=old_brand)

        weight = AgeWeight(tail_years=10)
        weight.debug = True

        profile = PipelineProfile(age=25)

        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment_young)
            apply_fn(garment_mature)
            apply_fn(garment_old)

        assert weight.get_explanations(garment_young)
        assert weight.get_explanations(garment_mature)
        assert not weight.get_explanations(garment_old)

    def test_debug_flag(self, garment_40_to_50):
        """It does not log explanations when debug mode is not enabled."""
        profile = PipelineProfile(age=45)

        weight = AgeWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment_40_to_50)

        assert not weight.get_explanations(garment_40_to_50)
