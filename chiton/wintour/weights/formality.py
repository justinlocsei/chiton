from chiton.closet.models import Garment
from chiton.runway.models import Formality
from chiton.wintour import build_choice_weights_lookup
from chiton.wintour.data import EXPECTATION_FREQUENCIES
from chiton.wintour.weights import BaseWeight


# The order of importance for formality expectations
EXPECTATION_FREQUENCY_ORDER = ('NEVER', 'RARELY', 'SOMETIMES', 'OFTEN', 'ALWAYS')


class FormalityWeight(BaseWeight):
    """A weight that gives preference to garments that match a user's formality."""

    name = 'Formality'
    slug = 'formality'

    def provide_profile_data(self, profile):
        frequency_weights = build_choice_weights_lookup(EXPECTATION_FREQUENCY_ORDER, EXPECTATION_FREQUENCIES)

        garment_formalities = {}
        formality_weights = {}
        formality_names = {}

        # Create a lookup table mapping garment primary keys to sets containing
        # the slugs of all formalities associated with the garment
        for garment_formality in Garment.formalities.through.objects.all().select_related('formality'):
            garment_pk = garment_formality.garment_id
            garment_formalities.setdefault(garment_pk, set())
            garment_formalities[garment_pk].add(garment_formality.formality.slug)

        # Create a lookup table for formality names for use in debug logging
        if self.debug:
            for formality in Formality.objects.all():
                formality_names[formality.slug] = formality.name

        # Create a lookup exposing the importance of the user's formality
        # expectations as weights
        for formality_slug, frequency in profile.expectations.items():
            formality_weights[formality_slug] = frequency_weights[frequency]

        return {
            'formality_names': formality_names,
            'formality_weights': formality_weights,
            'garment_formalities': garment_formalities
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
