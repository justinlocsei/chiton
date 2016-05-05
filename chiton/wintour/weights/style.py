from chiton.closet.models import Garment
from chiton.runway.models import Style
from chiton.wintour.weights import BaseWeight


MATCH_WEIGHT = 1


class StyleWeight(BaseWeight):
    """A weight that gives preference to garments matching a user's styles."""

    name = 'Style'
    slug = 'style'

    def provide_profile_data(self, profile):
        garment_styles = {}
        style_names = {}

        # Create a lookup table mapping garment primary keys to sets containing
        # the slugs of all styles associated with the garment
        for garment_style in Garment.styles.through.objects.all().select_related('style'):
            garment_pk = garment_style.garment_id
            garment_styles.setdefault(garment_pk, set())
            garment_styles[garment_pk].add(garment_style.style.slug)

        # Create a lookup table for style names for use in debug logging
        if self.debug:
            for style in Style.objects.all():
                style_names[style.slug] = style.name

        return {
            'garment_styles': garment_styles,
            'styles': set(profile.styles),
            'style_names': style_names
        }

    def apply(self, garment, garment_styles=None, styles=None, style_names=None):
        matching_styles = styles - garment_styles[garment.pk]
        match_count = len(matching_styles)

        if self.debug and match_count:
            for match in sorted(matching_styles):
                reason = 'The garment matches the user style of %s' % style_names[match].lower()
                self.explain_weight(garment, MATCH_WEIGHT, reason)

        return match_count * MATCH_WEIGHT
