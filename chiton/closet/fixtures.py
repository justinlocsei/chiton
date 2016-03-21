from chiton.closet.models import Brand
from chiton.core.data import Fixture


def load_fixtures():
    return [
        Fixture(Brand, Brand.objects.all())
    ]
