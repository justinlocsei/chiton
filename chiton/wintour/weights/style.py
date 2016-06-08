from chiton.closet.models import Garment
from chiton.runway.models import Style
from chiton.wintour.weights import BaseWeight


# The weight to add for each matching style
MATCH_WEIGHT = 1


class StyleWeight(BaseWeight):
    """A weight that gives preference to garments matching a user's styles."""

    name = 'Style'
    slug = 'style'

    def provide_profile_data(self, profile):
        styles_by_garment = {}
        style_names = {}

        # Create a lookup table mapping garment primary keys to sets containing
        # the slugs of all styles associated with the garment
        garment_styles = (
            Garment.styles.through
            .objects.all()
            .select_related('style')
            .values_list('garment_id', 'style__slug')
        )
        for garment_style in garment_styles:
            garment_pk = garment_style[0]
            style_slug = garment_style[1]
            try:
                styles_by_garment[garment_pk].add(style_slug)
            except KeyError:
                styles_by_garment[garment_pk] = set([style_slug])

        # Create a lookup table of style names for use in debug logging
        if self.debug:
            for style in Style.objects.all():
                style_names[style.slug] = style.name

        return {
            'garment_styles': styles_by_garment,
            'profile_styles': set(profile['styles']),
            'style_names': style_names
        }

    def apply(self, garment, garment_styles=None, profile_styles=None, style_names=None):
        matching_styles = profile_styles & garment_styles.get(garment.pk, set())
        match_count = len(matching_styles)

        if self.debug and match_count:
            for match in sorted(matching_styles):
                reason = 'The garment matches the user style of %s' % style_names[match].lower()
                self.explain_weight(garment, MATCH_WEIGHT, reason)

        return match_count * MATCH_WEIGHT
