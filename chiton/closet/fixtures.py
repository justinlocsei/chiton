from chiton.closet.apps import Config as App
from chiton.closet.models import Formality, Style
from chiton.core.data import Fixture


def load_fixtures():
    return [
        Fixture(App, 'formalities', Formality.objects.all()),
        Fixture(App, 'styles', Style.objects.all())
    ]
