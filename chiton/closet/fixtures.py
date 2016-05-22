from chiton.closet.models import CanonicalSize, Color, StandardSize
from chiton.core.data import Fixture


def load_fixtures():
    return [
        Fixture(CanonicalSize, CanonicalSize.objects.all()),
        Fixture(Color, Color.objects.all()),
        Fixture(StandardSize, StandardSize.objects.all())
    ]
