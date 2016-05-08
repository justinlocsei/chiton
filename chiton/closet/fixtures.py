from chiton.closet.models import Brand, Color, Size
from chiton.core.data import Fixture


def load_fixtures():
    return [
        Fixture(Brand, Brand.objects.all()),
        Fixture(Color, Color.objects.all()),
        Fixture(Size, Size.objects.all())
    ]
