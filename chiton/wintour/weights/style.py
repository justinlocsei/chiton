from chiton.closet.models import Garment
from chiton.wintour.weights import BaseWeight


class StyleWeight(BaseWeight):
    """A weight that gives preference to garments matching a user's styles."""

    name = 'Style'
    slug = 'style'

    def provide_profile_data(self, profile):
        garment_styles = {}

        # Create a lookup table mapping garment primary keys to sets containing
        # the slugs of all styles associated with the garment
        for garment_style in Garment.styles.through.objects.all().select_related('style'):
            garment_pk = garment_style.garment_id
            garment_styles.setdefault(garment_pk, set())
            garment_styles[garment_pk].add(garment_style.style.slug)

        return {
            'garment_styles': garment_styles,
            'styles': set(profile.styles)
        }

    def apply(self, garment, garment_styles=None, styles=None):
        matching_styles = styles - garment_styles[garment.pk]
        return len(matching_styles)
