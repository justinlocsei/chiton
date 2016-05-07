from chiton.wintour.weights import BaseWeight


# The static weight to use for featured items
WEIGHT = 1


class FeaturedWeight(BaseWeight):
    """A weight that gives a constant boost to any featured garments."""

    name = 'Featured'
    slug = 'featured'

    def apply(self, garment):
        weight = WEIGHT * garment.is_featured

        if self.debug and weight:
            self.explain_weight(garment, weight, 'The garment is marked as featured')

        return weight
