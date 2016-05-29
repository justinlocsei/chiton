from chiton.closet.data import CARE_CHOICES
from chiton.wintour.weights import BaseWeight


# The weight to apply to garments whose care is in a blacklist
BLACKLIST_WEIGHT = -1


class CareWeight(BaseWeight):
    """A weight that gives preference to garments based on their care instructions."""

    name = 'Care'
    slug = 'care'

    def provide_profile_data(self, profile):
        care_names = {}
        for choice in CARE_CHOICES:
            care_names[choice[0]] = choice[1].lower()

        return {
            'avoid_care': set(profile.avoid_care),
            'care_names': care_names
        }

    def apply(self, garment, avoid_care=None, care_names=None):
        weight = None
        if garment.care in avoid_care:
            weight = BLACKLIST_WEIGHT

        if self.debug and weight:
            reason = 'The garment has a care type of %s' % care_names[garment.care]
            self.explain_weight(garment, weight, reason)

        return weight or 0
