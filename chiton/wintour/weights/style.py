from chiton.wintour.weights import BaseWeight


class StyleWeight(BaseWeight):
    """A weight that gives preference to garments matching a user's styles."""

    name = 'Style'
    slug = 'style'

    def provide_profile_data(self, profile):
        return {
            'styles': set([style.slug for style in profile.styles.all()])
        }

    def apply(self, garment, styles=None):
        garment_styles = set([style.slug for style in garment.styles.all()])
        matching_styles = styles - garment_styles

        return len(matching_styles)
