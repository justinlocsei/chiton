from itertools import chain

import chiton.closet.fixtures as closet
import chiton.rack.fixtures as rack
import chiton.runway.fixtures as runway

# All known application fixtures
APP_FIXTURES = [closet, rack, runway]


def load_fixtures():
    """Expose a combined, flattened list of all app fixtures.

    Returns:
        list: Fixture instances for all applications
    """
    fixtures = [f.load_fixtures() for f in APP_FIXTURES]
    return list(chain.from_iterable(fixtures))
