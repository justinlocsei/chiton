import pytest

from chiton.wintour.data import EXPECTATION_FREQUENCIES
from chiton.wintour.weights.formality import FormalityWeight


@pytest.mark.django_db
class TestFormalityWeight:

    def test_no_matches(self, formality_factory, garment_factory, pipeline_profile_factory):
        """It returns a null weight when a garment's formalities do not match the user's."""
        casual = formality_factory(slug='casual')
        formality_factory(slug='executive')

        garment = garment_factory(formalities=[casual])
        profile = pipeline_profile_factory(expectations=[{
            'formality': 'executive',
            'frequency': EXPECTATION_FREQUENCIES['NEVER']
        }])

        weight = FormalityWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            result = apply_fn(garment)
            assert not result

    def test_matches(self, formality_factory, garment_factory, pipeline_profile_factory):
        """It gives weight to garments that match the user's formalities based on the frequency of the formality."""
        casual = formality_factory(slug='casual')
        garment = garment_factory(formalities=[casual])

        weight = FormalityWeight()
        frequency_order = ('NEVER', 'RARELY', 'SOMETIMES', 'OFTEN', 'ALWAYS')

        results = {}
        for frequency in frequency_order:
            profile = pipeline_profile_factory(expectations=[{
                'formality': 'casual',
                'frequency': EXPECTATION_FREQUENCIES[frequency]
            }])

            with weight.apply_to_profile(profile) as apply_fn:
                results[frequency] = apply_fn(garment)

        assert not results['NEVER']
        assert results['RARELY']
        assert results['RARELY'] < results['SOMETIMES'] < results['OFTEN'] < results['ALWAYS']

    def test_matches_multiple(self, formality_factory, garment_factory, pipeline_profile_factory):
        """It adds weight for each matching formality."""
        business = formality_factory(slug='business')
        executive = formality_factory(slug='executive')

        dress = garment_factory(formalities=[business])
        blazer = garment_factory(formalities=[business, executive])

        profile = pipeline_profile_factory(expectations=[
            {'formality': 'business', 'frequency': EXPECTATION_FREQUENCIES['SOMETIMES']},
            {'formality': 'executive', 'frequency': EXPECTATION_FREQUENCIES['SOMETIMES']}
        ])

        weight = FormalityWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            dress_weight = apply_fn(dress)
            blazer_weight = apply_fn(blazer)

        assert dress_weight
        assert blazer_weight
        assert blazer_weight > dress_weight

    def test_debug(self, formality_factory, garment_factory, pipeline_profile_factory):
        """It logs explanations for any garments that match a formality."""
        casual = formality_factory(slug='casual')
        executive = formality_factory(slug='executive')

        garment_hit = garment_factory(formalities=[casual])
        garment_miss = garment_factory(formalities=[executive])

        profile = pipeline_profile_factory(expectations=[{
            'formality': 'casual',
            'frequency': EXPECTATION_FREQUENCIES['RARELY']
        }])

        weight = FormalityWeight()
        weight.debug = True

        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment_hit)
            apply_fn(garment_miss)

        assert weight.get_explanations(garment_hit)
        assert not weight.get_explanations(garment_miss)

    def test_debug_flag(self, formality_factory, garment_factory, pipeline_profile_factory):
        """It does not log explanations when debug mode is not enabled."""
        casual = formality_factory(slug='casual')
        garment = garment_factory(formalities=[casual])

        profile = pipeline_profile_factory(expectations=[{
            'formality': 'casual',
            'frequency': EXPECTATION_FREQUENCIES['RARELY']
        }])

        weight = FormalityWeight()
        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment)

        assert not weight.get_explanations(garment)
