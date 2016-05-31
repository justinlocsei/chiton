import pytest

from chiton.wintour.weights.style import StyleWeight


@pytest.mark.django_db
class TestStyleWeight:

    def test_no_matches(self, garment_factory, pipeline_profile_factory, style_factory):
        """It returns a null weight when no garment styles match."""
        style_factory(slug='casual')
        classy = style_factory(slug='classy')

        garment = garment_factory(styles=[classy])
        profile = pipeline_profile_factory(styles=['casual'])

        weight = StyleWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            result = apply_fn(garment)

            assert not result

    def test_match(self, garment_factory, pipeline_profile_factory, style_factory):
        """It adds weight for each garment-style match."""
        casual = style_factory(slug='casual')
        classy = style_factory(slug='classy')

        garment_single_match = garment_factory(styles=[classy])
        garment_multi_match = garment_factory(styles=[classy, casual])
        profile = pipeline_profile_factory(styles=['casual', 'classy'])

        weight = StyleWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            single_weight = apply_fn(garment_single_match)
            multi_weight = apply_fn(garment_multi_match)

            assert single_weight
            assert multi_weight > single_weight

    def test_debug(self, garment_factory, pipeline_profile_factory, style_factory):
        """It logs explanations for any garments that match a style."""
        casual = style_factory(slug='casual')

        garment_match = garment_factory(styles=[casual])
        garment_miss = garment_factory(styles=[])
        profile = pipeline_profile_factory(styles=['casual'])

        weight = StyleWeight()
        weight.debug = True

        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment_match)
            apply_fn(garment_miss)

        assert weight.get_explanations(garment_match)
        assert not weight.get_explanations(garment_miss)

    def test_debug_flag(self, garment_factory, pipeline_profile_factory, style_factory):
        """It does not log explanations when debug mode is not enabled."""
        casual = style_factory(slug='casual')

        garment_match = garment_factory(styles=[casual])
        profile = pipeline_profile_factory(styles=['casual'])

        weight = StyleWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment_match)

        assert not weight.get_explanations(garment_match)
