from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_loose_range(lower, upper):
    """Validate a loose range of integers.

    Args:
        lower (int): The possible lower bound for the range
        upper (int): The possible upper bound for the range

    Raises:
        django.core.exceptions.ValidationError: If the range is improperly ordered
    """
    if lower is not None and upper is not None:
        if upper < lower:
            raise ValidationError(
                _('Ensure that %(upper)d comes before %(lower)d'),
                params={'lower': lower, 'upper': upper})
