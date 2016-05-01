from chiton.wintour.weights import BaseWeight


class AgeWeight(BaseWeight):
    """A weight that compares a user's age with a brand's target age."""

    name = 'Age'
    slug = 'age'
