from chiton.runway.models import Basic, Category, Formality, Propriety, Style
from chiton.core.data import Fixture


def load_fixtures():
    return [
        Fixture(Category, Category.objects.all()),
        Fixture(Formality, Formality.objects.all()),
        Fixture(Style, Style.objects.all()),
        Fixture(Propriety, Propriety.objects.for_export()),
    ]
