import pytest

from chiton.wintour.weights.featured import FeaturedWeight


@pytest.mark.django_db
class TestFeaturedWeight:

    def test_no_matches(self, garment_factory, pipeline_profile_factory):
        """It returns a null weight when a garment is not featured."""
        garment = garment_factory(is_featured=False)
        profile = pipeline_profile_factory()

        weight = FeaturedWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            result = apply_fn(garment)
            assert not result

    def test_match(self, garment_factory, pipeline_profile_factory):
        """It adds a non-zero weight when a garment is featured."""
        garment = garment_factory(is_featured=True)
        profile = pipeline_profile_factory()

        weight = FeaturedWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            result = apply_fn(garment)
            assert result

    def test_debug(self, garment_factory, pipeline_profile_factory):
        """It logs explanations for any featured garments."""
        garment_featured = garment_factory(is_featured=True)
        garment_normal = garment_factory(is_featured=False)
        profile = pipeline_profile_factory()

        weight = FeaturedWeight()
        weight.debug = True

        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment_featured)
            apply_fn(garment_normal)

        assert weight.get_explanations(garment_featured)
        assert not weight.get_explanations(garment_normal)

    def test_debug_flag(self, garment_factory, pipeline_profile_factory):
        """It does not log explanations when debug mode is not enabled."""
        garment = garment_factory(is_featured=True)
        profile = pipeline_profile_factory()

        weight = FeaturedWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment)

        assert not weight.get_explanations(garment)
