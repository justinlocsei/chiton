from chiton.wintour.weights import BaseWeight


AGE_WEIGHT = 1
AGE_RANGE_MIN = 0
AGE_RANGE_MAX = 100


class AgeWeight(BaseWeight):
    """A weight that compares a user's age with a brand's target age."""

    name = 'Age'
    slug = 'age'

    def configure_weight(self, tail=3):
        """Create a new age weight.

        The tail keyword arg should be an integer specifying the number of years
        on either side of a brand's age range that should receive a weak boost.

        Keyword Args:
            tail (int): The number of years outside of an age range that should count as a weak match
        """
        self.tail = tail

    def prepare_garments(self, garments):
        return garments.select_related('brand')

    def provide_profile_data(self, profile):
        return {
            'age': profile.age
        }

    def apply(self, garment, age=None):
        brand = garment.brand

        lower_age = brand.age_lower or AGE_RANGE_MIN
        upper_age = brand.age_upper or AGE_RANGE_MAX
        is_in_range = lower_age <= age <= upper_age

        lower_tail = lower_age - self.tail
        upper_tail = upper_age + self.tail
        is_near_range = lower_tail <= age < lower_age or upper_age < age <= upper_tail

        return AGE_WEIGHT * is_near_range + AGE_WEIGHT * 2 * is_in_range
