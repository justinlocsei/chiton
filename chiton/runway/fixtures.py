from chiton.core.fixture import Fixture
from chiton.closet.models import Color
from chiton.runway.models import Basic, Category, Formality, Propriety, Style


BASIC_FIELDS = [
    'category',
    'name',
    'primary_color',
    'secondary_colors',
    'slug'
]


def load_fixtures():
    return [
        Fixture(Basic, initial=True, requires=[Category, Color], fields=BASIC_FIELDS),
        Fixture(Category),
        Fixture(Formality),
        Fixture(Propriety, queryset=Propriety.objects.for_export(), requires=[Basic, Formality]),
        Fixture(Style)
    ]
