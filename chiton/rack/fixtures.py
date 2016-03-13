from chiton.core.data import Fixture
from chiton.rack.apps import Config as App
from chiton.rack.models import AffiliateNetwork


def load_fixtures():
    return [
        Fixture(App, 'affiliate_networks', AffiliateNetwork.objects.all())
    ]
