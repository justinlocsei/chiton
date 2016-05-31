from chiton.core.fixture import Fixture
from chiton.runway.models import Category, Formality, Propriety, Style


def load_fixtures():
    return [
        Fixture(Category, Category.objects.all()),
        Fixture(Formality, Formality.objects.all()),
        Fixture(Propriety, Propriety.objects.for_export()),
        Fixture(Style, Style.objects.all())
    ]
