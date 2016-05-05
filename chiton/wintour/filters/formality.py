from chiton.runway.models import Formality, Propriety
from chiton.runway.data import PROPRIETY_IMPORTANCES
from chiton.wintour.data import EXPECTATION_FREQUENCIES
from chiton.wintour.filters import BaseFilter


# Rankings of expectation data, from least to most important
PROPRIETY_IMPORTANCE_ORDER = ('NOT', 'MILDLY', 'SOMEWHAT', 'VERY', 'ALWAYS')
EXPECTATION_FREQUENCY_ORDER = ('NEVER', 'RARELY', 'SOMETIMES', 'OFTEN', 'ALWAYS')


class FormalityFilter(BaseFilter):
    """A filter that excludes garments whose basic type is inappropriate.

    Appropriateness is determined by examining how strongly a basic is
    associated with the current level of formality and how frequently the user
    needs to dress at that level of formality.  Basics that are never used
    for a formality or that are of low importance for an infrequently needed
    formality will likely be excluded.
    """

    name = 'Formality'
    slug = 'formality'

    def configure(self, cutoff=None):
        """Create a new formality filter.

        The cutoff keyword arg should be a floating-point value expressing the
        percentage at which garments should be excluded based upon the
        importance of their basic type to a wardrobe profile.

        Keyword Args:
            cutoff (float): The cutoff value for excluding basics
        """
        self.cutoff = cutoff

    def provide_profile_data(self, profile):
        frequency_weights = self._build_choice_weights_lookup(EXPECTATION_FREQUENCY_ORDER, EXPECTATION_FREQUENCIES)
        importance_weights = self._build_choice_weights_lookup(PROPRIETY_IMPORTANCE_ORDER, PROPRIETY_IMPORTANCES)

        # Use the lowest non-zero value of the combined weights as the cutoff,
        # if no explicit cutoff for the filter has been provided
        cutoff = self.cutoff
        if cutoff is None:
            weight_values = list(frequency_weights.values()) + list(importance_weights.values())
            cutoff = min([v for v in weight_values if v])

        return {
            'cutoff': cutoff,
            'expectations': profile.expectations,
            'formality_count': Formality.objects.count(),
            'weights': {
                'formality': self._build_formality_weights_lookup(importance_weights),
                'frequency': frequency_weights
            }
        }

    def apply(self, garments, cutoff=None, expectations=None, formality_count=None, weights=None):
        formality_weights = weights['formality']
        frequency_weights = weights['frequency']

        # Build a lookup table mapping Basic primary keys to the number of times
        # that the weight for basic, as derived from the combination of the
        # formality/basic weight and the frequency/formality weight, falls below
        # the provided cutoff value
        basic_exclusions = {}
        for formality_slug, frequency in expectations.items():
            frequency_weight = frequency_weights[frequency]
            for basic_pk, basic_weight in formality_weights[formality_slug].items():
                total_weight = basic_weight * frequency_weight
                if total_weight < cutoff:
                    basic_exclusions.setdefault(basic_pk, 0)
                    basic_exclusions[basic_pk] += 1

        # Build a list of the primary keys of all basics that are excluded from
        # every level of formality
        excluded_basics = [
            basic_pk for basic_pk, exclusion_count in basic_exclusions.items()
            if exclusion_count == formality_count
        ]

        # Remove any garments associated with excluded basics, or just return
        # the original set of garments if no excluded basics are found
        if excluded_basics:
            return garments.exclude(basic__pk__in=excluded_basics)
        else:
            return garments

    def _build_choice_weights_lookup(self, choice_names, choices):
        """Create a lookup table mapping choice names to their weight.

        Args:
            choice_names (list): An ordered list of choice-name keys
            choices (dict): The dict defining the values for each choice key

        Returns:
            dict: A lookup exposing the weight of each choice name
        """
        lookup = {}

        total_choices = len(choice_names) - 1
        for i, choice_name in enumerate(choice_names):
            choice_weight = i / total_choices if total_choices else 0
            lookup[choices[choice_name]] = choice_weight

        return lookup

    def _build_formality_weights_lookup(self, importance_weights):
        """Create a lookup table mapping formalities to per-basic weights.

        Args:
            importance_weights (dict): A mapping of propriety importances to weights

        Returns:
            dict: A lookup table for formality/basic weights
        """
        lookup = {}
        proprieties = Propriety.objects.all().select_related('basic', 'formality')

        for propriety in proprieties:
            formality_slug = propriety.formality.slug
            lookup.setdefault(formality_slug, {})
            lookup[formality_slug][propriety.basic.pk] = importance_weights[propriety.importance]

        return lookup
