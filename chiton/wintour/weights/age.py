from chiton.wintour.weights import BaseWeight


# The base weight to apply for age matches
AGE_WEIGHT = 1

# Default values for missing brand age ranges for weighting calculations
AGE_RANGE_MIN = 0
AGE_RANGE_MAX = 100


class AgeWeight(BaseWeight):
    """A weight that compares a user's age with a brand's target age."""

    name = 'Age'
    slug = 'age'

    def configure_weight(self, tail_years=3):
        """Create a new age weight.

        The `tail_years` keyword arg should be an integer specifying the number
        of years on either side of a brand's age range that should receive a
        weak boost.

        Keyword Args:
            tail_years (int): The number of years outside of an age range that should count as a weak match
        """
        self.tail_years = tail_years

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

        lower_tail = lower_age - self.tail_years
        upper_tail = upper_age + self.tail_years
        is_near_range = lower_tail <= age < lower_age or upper_age < age <= upper_tail

        in_range_weight = AGE_WEIGHT * 2 * is_in_range
        near_range_weight = AGE_WEIGHT * is_near_range
        weight = in_range_weight + near_range_weight

        if self.debug and weight:
            brand_range = "%s's age range of %d-%d" % (brand.name, brand.age_lower, brand.age_upper)

            if is_in_range:
                reason = '%s includes %d' % (brand_range, age)
            else:
                reason = '%s is within %d years of %d' % (brand_range, self.tail_years, age)

            self.explain_weight(garment, weight, reason)

        return weight
