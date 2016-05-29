from chiton.wintour import build_choice_weights_lookup


class TestBuildChoiceWeightsLookup:

    def test_build_lookup(self):
        """It builds a lookup mapping choice IDs to weights based on their order."""
        choices = [
            ('one', 'One'),
            ('two', 'Two'),
            ('three', 'Three')
        ]

        lookup = build_choice_weights_lookup(choices)

        assert lookup['one'] == 0
        assert lookup['two'] == 0.5
        assert lookup['three'] == 1

    def test_max_weight(self):
        """It uses the max weight to scale the choice weights."""
        choices = [
            ('one', 'One'),
            ('two', 'Two')
        ]

        lookup = build_choice_weights_lookup(choices, max_weight=2)

        assert lookup['one'] == 0
        assert lookup['two'] == 2

    def test_single_choice(self):
        """It gives a single choice the maximum weight."""
        lookup = build_choice_weights_lookup([('one', 'One')], max_weight=3)

        assert lookup['one'] == 3
