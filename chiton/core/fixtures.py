from collections import OrderedDict
from itertools import chain

import chiton.closet.fixtures as closet
import chiton.rack.fixtures as rack
import chiton.runway.fixtures as runway


# All known application fixtures
APP_FIXTURES = [closet, rack, runway]


class CircularDependencyError(Exception):
    """An error raised when fixtures specify circular dependencies."""


def load_fixtures():
    """Expose a combined, flattened list of all app fixtures.

    The fixtures are ordered so that any models required by a fixture are loaded
    before that fixture.

    Returns:
        list[chiton.core.fixture.Fixture]: Fixture instances for all applications
    """
    fixtures = [f.load_fixtures() for f in APP_FIXTURES]
    combined = list(chain.from_iterable(fixtures))

    return order_fixtures_by_dependency(combined)


def order_fixtures_by_dependency(fixtures):
    """Order a list of fixtures by their dependencies.

    Args:
        fixtures (list[chiton.core.fixture.Fixture]): All fixture instances to order

    Returns:
        list[chiton.core.fixture.Fixture]: The fixtures ordered by dependency
    """
    def add_fixture(fixture, ordered, before=None):
        for required_model in fixture.requires:
            model_fixtures = [f for f in fixtures if f.model_class == required_model]
            for model_fixture in model_fixtures:
                if fixture.model_class in model_fixture.requires:
                    raise CircularDependencyError('The %s fixture requires %s models, which require the %s fixture' % (
                        fixture.label,
                        required_model._meta.verbose_name,
                        model_fixture.label
                    ))
                else:
                    add_fixture(model_fixture, ordered, before=fixture)

        try:
            insert_at = ordered.index(before)
        except ValueError:
            insert_at = len(ordered)

        ordered.insert(insert_at, fixture)

    ordered = []
    for fixture in fixtures:
        add_fixture(fixture, ordered)

    deduped = OrderedDict()
    for fixture in ordered:
        deduped[fixture.label] = fixture

    return list(deduped.values())
