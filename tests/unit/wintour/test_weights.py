import pytest

from chiton.wintour.weights import BaseWeight


class TestWeight(BaseWeight):
    name = 'Test'
    slug = 'test'


class TestBaseWeight:

    def test_importance(self):
        """It can receive a per-instance importance."""
        weight = TestWeight(importance=3)
        assert weight.importance == 3

    def test_importance_kwargs(self):
        """It does not pass its importance to a weight subclass's configuration method."""
        class Weight(TestWeight):

            def configure_weight(self, custom=None):
                self.custom = custom

        weight = Weight(importance=5, custom='custom')
        assert weight.custom == 'custom'

    @pytest.mark.django_db
    def test_explain_weight(self, garment_factory):
        """It adds log messages explaining a garment's weight."""
        garment_one = garment_factory()
        garment_two = garment_factory()

        weight = TestWeight()
        weight.explain_weight(garment_one, 1.0, 'hit')
        weight.explain_weight(garment_two, 0.0, 'miss')

        assert weight.get_explanations(garment_one) == [{'weight': 1.0, 'reason': 'hit'}]
        assert weight.get_explanations(garment_two) == [{'weight': 0.0, 'reason': 'miss'}]

    @pytest.mark.django_db
    def test_apply_default(self, garment_factory):
        """It returns a default weight of zero for a given garment."""
        garment = garment_factory()

        weight = TestWeight()
        applied = weight.apply(garment)

        assert applied == 0
