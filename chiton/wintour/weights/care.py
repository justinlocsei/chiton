from chiton.closet.data import CARE_TYPES
from chiton.wintour.weights import BaseWeight


# The weight to apply to garments whose care is in a blacklist
BLACKLIST_WEIGHT = -1

# Readable names for blacklisted care types
CARE_NAMES = {
    CARE_TYPES['HAND_WASH']: 'hand washing',
    CARE_TYPES['DRY_CLEAN']: 'dry cleaning'
}


class CareWeight(BaseWeight):
    """A weight that gives preference to garments based on their care instructions."""

    name = 'Care'
    slug = 'care'

    def provide_profile_data(self, profile):
        return {
            'avoid_care': set(profile.avoid_care)
        }

    def apply(self, garment, avoid_care=None):
        weight = None
        if garment.care in avoid_care:
            weight = BLACKLIST_WEIGHT

        if self.debug and weight:
            reason = 'The garment requires %s' % CARE_NAMES[garment.care]
            self.explain_weight(garment, weight, reason)

        return weight or 0
