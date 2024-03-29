import pytest

from chiton.core.fixture import Fixture
from chiton.core.fixtures import CircularDependencyError, load_fixtures, order_fixtures_by_dependency
from chiton.closet.models import Brand, Color, Garment
from chiton.runway.models import Style


@pytest.mark.django_db
class TestLoadFixtures:

    def test_flat_list(self):
        """It returns a flat list of all fixtures."""
        fixtures = load_fixtures()

        assert len(fixtures) > 0
        assert len([f for f in fixtures if isinstance(f, Fixture)]) == len(fixtures)


class TestOrderFixturesByDependency:

    def order_with_labels(self, fixtures):
        ordered = order_fixtures_by_dependency(fixtures)
        return [f.label for f in ordered]

    def test_no_dependencies(self):
        """It returns an unmodified list when no fixtures have dependencies."""
        fixtures = [Fixture(Brand), Fixture(Color)]
        assert self.order_with_labels(fixtures) == ['brand', 'color']

    def test_dependencies(self):
        """It ensures that dependencies come before their parent fixtures."""
        fixtures = [
            Fixture(Garment, requires=[Color]),
            Fixture(Color)
        ]

        assert self.order_with_labels(fixtures) == ['color', 'garment']

    def test_dependencies_multiple(self):
        """It uses left-to-right ordering for multiple dependencies."""
        fixtures = [
            Fixture(Garment, requires=[Brand, Style]),
            Fixture(Color),
            Fixture(Brand),
            Fixture(Style, requires=[Color])
        ]

        assert self.order_with_labels(fixtures) == ['brand', 'color', 'style', 'garment']

    def test_dependencies_nested(self):
        """It ensures a correct order for nested dependencies."""
        fixtures = [
            Fixture(Garment, requires=[Color]),
            Fixture(Color),
            Fixture(Brand, requires=[Garment])
        ]

        assert self.order_with_labels(fixtures) == ['color', 'garment', 'brand']

    def test_dependencies_shared(self):
        """It respects the order of fixtures that share dependencies."""
        fixtures = [
            Fixture(Garment, requires=[Color]),
            Fixture(Color),
            Fixture(Brand, requires=[Color])
        ]

        assert self.order_with_labels(fixtures) == ['color', 'garment', 'brand']

    def test_dependencies_shared_nested(self):
        """It ensures a correct order for nested shared dependencies."""
        fixtures = [
            Fixture(Garment, requires=[Brand, Style]),
            Fixture(Color),
            Fixture(Brand, requires=[Color]),
            Fixture(Style, requires=[Brand])
        ]

        assert self.order_with_labels(fixtures) == ['color', 'brand', 'style', 'garment']

    def test_dependencies_missing(self):
        """It ignores required models that lack a fixture."""
        fixtures = [
            Fixture(Garment, requires=[Brand]),
            Fixture(Color)
        ]

        assert self.order_with_labels(fixtures) == ['garment', 'color']

    def test_dependencies_circular(self):
        """It raises an error when circular dependencies are detected."""
        fixtures = [
            Fixture(Garment, requires=[Color]),
            Fixture(Color, requires=[Garment])
        ]

        with pytest.raises(CircularDependencyError):
            order_fixtures_by_dependency(fixtures)

    def test_dependencies_circular_self(self):
        """It raises an error when self-referential dependencies are detected."""
        fixtures = [Fixture(Color, requires=[Color])]

        with pytest.raises(CircularDependencyError):
            order_fixtures_by_dependency(fixtures)
