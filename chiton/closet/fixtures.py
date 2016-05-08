from chiton.closet.models import Color, Size
from chiton.core.data import Fixture


def load_fixtures():
    return [
        Fixture(Color, Color.objects.all()),
        Fixture(Size, Size.objects.all())
    ]
