from chiton.closet.models import CanonicalSize, Color, StandardSize
from chiton.core.fixture import Fixture


def load_fixtures():
    return [
        Fixture(CanonicalSize, CanonicalSize.objects.all()),
        Fixture(Color, Color.objects.all()),
        Fixture(StandardSize, StandardSize.objects.all(), requires=[CanonicalSize])
    ]
