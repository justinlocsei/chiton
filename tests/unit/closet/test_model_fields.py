from chiton.closet.data import EMPHASES, EMPHASIS_CHOICES
from chiton.closet.model_fields import EmphasisField


class TestEmphasisField:

    def test_choices(self):
        """It uses emphasis choices."""
        field = EmphasisField()
        assert field.choices == EMPHASIS_CHOICES

    def test_default(self):
        """It defaults to a neutral emphasis."""
        field = EmphasisField()
        assert field.default == EMPHASES['NEUTRAL']

    def test_default_override(self):
        """It allows a custom default to be used."""
        field = EmphasisField(default=EMPHASES['WEAK'])
        assert field.default == EMPHASES['WEAK']
