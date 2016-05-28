from chiton.runway.models import Category, Formality, Propriety, Style
from chiton.core.data import Fixture


def load_fixtures():
    return [
        Fixture(Category, Category.objects.all()),
        Fixture(Formality, Formality.objects.all()),
        Fixture(Propriety, Propriety.objects.for_export()),
        Fixture(Style, Style.objects.all())
    ]
