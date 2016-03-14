from chiton.core.data import Fixture
from chiton.rack.models import AffiliateNetwork


def load_fixtures():
    return [
        Fixture(AffiliateNetwork, AffiliateNetwork.objects.all())
    ]
