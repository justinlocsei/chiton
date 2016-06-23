from chiton.core.fixture import Fixture
from chiton.closet.models import Color
from chiton.runway.models import Basic, Category, Formality, Propriety, Style


def load_fixtures():
    return [
        Fixture(Basic, Basic.objects.all(), initial=True, requires=[Category, Color]),
        Fixture(Category, Category.objects.all()),
        Fixture(Formality, Formality.objects.all()),
        Fixture(Propriety, Propriety.objects.for_export(), requires=[Basic, Formality]),
        Fixture(Style, Style.objects.all())
    ]
