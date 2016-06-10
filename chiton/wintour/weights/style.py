from chiton.closet.models import Garment
from chiton.core.queries import cache_query
from chiton.runway.models import Style
from chiton.wintour.weights import BaseWeight


# The weight to add for each matching style
MATCH_WEIGHT = 1


class StyleWeight(BaseWeight):
    """A weight that gives preference to garments matching a user's styles."""

    name = 'Style'
    slug = 'style'

    def provide_profile_data(self, profile):
        if self.debug:
            style_names = _build_style_names_lookup()
        else:
            style_names = {}

        return {
            'garment_styles': _build_garment_styles_lookup(),
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


@cache_query(Garment, Style)
def _build_garment_styles_lookup():
    """Create a lookup table mapping garment IDs to sets of style slugs.

    Returns:
        dict[int, set[str]]: A lookup table of garment styles
    """
    garment_styles = (
        Garment.styles.through
        .objects.all()
        .select_related('style')
        .values_list('garment_id', 'style__slug')
    )

    lookup = {}
    for garment_style in garment_styles:
        garment_pk = garment_style[0]
        style_slug = garment_style[1]
        try:
            lookup[garment_pk].add(style_slug)
        except KeyError:
            lookup[garment_pk] = set([style_slug])

    return lookup


@cache_query(Style)
def _build_style_names_lookup():
    """Create a lookup table mapping style slugs to names.

    Returns:
        dict[str, str]: A lookup table for style names
    """
    lookup = {}
    for style in Style.objects.all():
        lookup[style.slug] = style.name

    return lookup
