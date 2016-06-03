from chiton.core.fixture import Fixture
from chiton.core.fixtures import load_fixtures


class TestLoadFixtures:

    def test_flat_list(self):
        """It returns a flat list of all fixtures."""
        fixtures = load_fixtures()

        assert len(fixtures) > 0
        assert len([f for f in fixtures if isinstance(f, Fixture)]) == len(fixtures)
