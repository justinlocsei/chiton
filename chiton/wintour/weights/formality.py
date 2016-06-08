from chiton.closet.models import Garment
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

        formalities_by_garment = {}
        formality_weights = {}
        formality_names = {}

        # Create a lookup table mapping garment primary keys to sets containing
        # the slugs of all formalities associated with the garment
        garment_formalities = (
            Garment.formalities.through
            .objects.all()
            .select_related('formality')
            .values_list('garment_id', 'formality__slug')
        )
        for garment_formality in garment_formalities:
            garment_pk = garment_formality[0]
            formality_slug = garment_formality[1]
            try:
                formalities_by_garment[garment_pk].add(formality_slug)
            except KeyError:
                formalities_by_garment[garment_pk] = set([formality_slug])

        # Create a lookup table for formality names for use in debug logging
        if self.debug:
            for formality in Formality.objects.all():
                formality_names[formality.slug] = formality.name

        # Create a lookup exposing the importance of the user's formality
        # expectations as weights
        for formality_slug, frequency in profile['expectations'].items():
            formality_weights[formality_slug] = frequency_weights[frequency]

        return {
            'formality_names': formality_names,
            'formality_weights': formality_weights,
            'garment_formalities': formalities_by_garment
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
