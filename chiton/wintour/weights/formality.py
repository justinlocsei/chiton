from chiton.closet.models import Garment
from chiton.core.queries import cache_query
from chiton.runway.models import Formality
from chiton.wintour import build_choice_weights_lookup
from chiton.wintour.data import EXPECTATION_FREQUENCY_CHOICES
from chiton.wintour.weights import BaseWeight


class FormalityWeight(BaseWeight):
    """A weight that gives preference to garments that match a user's formality."""

    name = 'Formality'
    slug = 'formality'

    def provide_profile_data(self, profile):
        frequency_weights = build_choice_weights_lookup(EXPECTATION_FREQUENCY_CHOICES)

        # Create a lookup for formalilty names for use in debug logging
        if self.debug:
            formality_names = _build_formality_name_lookup()
        else:
            formality_names = {}

        # Create a lookup exposing the importance of the user's formality
        # expectations as weights
        formality_weights = {}
        for formality_slug, frequency in profile['expectations'].items():
            formality_weights[formality_slug] = frequency_weights[frequency]

        return {
            'formality_names': formality_names,
            'formality_weights': formality_weights,
            'garment_formalities': _build_garment_formality_lookup()
        }

    def apply(self, garment, formality_weights=None, formality_names=None, garment_formalities=None):
        total_weight = 0

        formalities = garment_formalities.get(garment.pk, [])
        for formality_slug in formalities:
            importance = formality_weights.get(formality_slug, 0)
            total_weight += importance

            if self.debug and importance:
                reason = 'The garment is %s, which the user wears %d%% of the time' % (
                    formality_names[formality_slug].lower(),
                    importance * 100
                )
                self.explain_weight(garment, importance, reason)

        return total_weight


@cache_query(Formality, Garment)
def _build_garment_formality_lookup():
    """Create a lookup table that maps garment IDs to sets of formality slugs.

    Returns:
        dict[int, set[str]]: A lookup table for garment formalities
    """
    garment_formalities = (
        Garment.formalities.through
        .objects.all()
        .select_related('formality')
        .values_list('garment_id', 'formality__slug')
    )

    lookup = {}
    for garment_formality in garment_formalities:
        garment_pk = garment_formality[0]
        formality_slug = garment_formality[1]
        try:
            lookup[garment_pk].add(formality_slug)
        except KeyError:
            lookup[garment_pk] = set([formality_slug])

    return lookup


@cache_query(Formality)
def _build_formality_name_lookup():
    """Create a lookup table that maps formality slugs to names.

    Returns:
        dict[str, str]: A lookup table for formality names
    """
    lookup = {}
    for formality in Formality.objects.all():
        lookup[formality.slug] = formality.name

    return lookup
