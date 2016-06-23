from chiton.closet.models import CanonicalSize, Color, StandardSize
from chiton.core.fixture import Fixture


def load_fixtures():
    return [
        Fixture(CanonicalSize),
        Fixture(Color),
        Fixture(StandardSize, requires=[CanonicalSize])
    ]
