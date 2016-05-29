import pytest

from chiton.closet.data import CARE_TYPES
from chiton.wintour.pipeline import PipelineProfile
from chiton.wintour.weights.care import CareWeight


@pytest.mark.django_db
class TestCareWeight:

    def test_no_matches(self, garment_factory):
        """It returns a null weight when a garment's care type is not blacklisted."""
        garment = garment_factory(care=CARE_TYPES['HAND_WASH'])
        profile = PipelineProfile(avoid_care=[CARE_TYPES['DRY_CLEAN']])

        weight = CareWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            result = apply_fn(garment)
            assert not result

    def test_blacklist(self, garment_factory):
        """It uses a negative weight when a garment's care type is blacklisted."""
        garment = garment_factory(care=CARE_TYPES['DRY_CLEAN'])
        profile = PipelineProfile(avoid_care=[CARE_TYPES['DRY_CLEAN']])

        weight = CareWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            result = apply_fn(garment)
            assert result < 0

    def test_blacklist_multiple(self, garment_factory):
        """It accepts multiple values to blacklist."""
        garment = garment_factory(care=CARE_TYPES['DRY_CLEAN'])
        profile = PipelineProfile(avoid_care=[CARE_TYPES['DRY_CLEAN'], CARE_TYPES['HAND_WASH']])

        weight = CareWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            result = apply_fn(garment)
            assert result < 0

    def test_debug(self, garment_factory):
        """It logs explanations for any garments with blacklisted care types."""
        garment_blacklist = garment_factory(care=CARE_TYPES['DRY_CLEAN'])
        garment_normal = garment_factory(care=CARE_TYPES['HAND_WASH'])
        profile = PipelineProfile(avoid_care=[CARE_TYPES['DRY_CLEAN']])

        weight = CareWeight()
        weight.debug = True

        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment_blacklist)
            apply_fn(garment_normal)

        assert weight.get_explanations(garment_blacklist)
        assert not weight.get_explanations(garment_normal)

    def test_debug_flag(self, garment_factory):
        """It does not log explanations when debug mode is not enabled."""
        garment = garment_factory(care=CARE_TYPES['DRY_CLEAN'])
        profile = PipelineProfile(avoid_care=[CARE_TYPES['DRY_CLEAN']])

        weight = CareWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment)

        assert not weight.get_explanations(garment)
