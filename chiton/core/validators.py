from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_range(lower, upper, loose=False):
    """Validate a range of integers.

    Args:
        lower (int): The possible lower bound for the range
        upper (int): The possible upper bound for the range

    Keyword Args:
        loose (bool): Whether the range can be open-ended on either side

    Raises:
        django.core.exceptions.ValidationError: If the range is improperly ordered
    """
    if not loose:
        if lower is None:
            raise ValidationError(_('Ensure that the range has a lower bound'))
        elif upper is None:
            raise ValidationError(_('Ensure that the range has an upper bound'))

    if lower is not None and upper is not None:
        if upper < lower:
            raise ValidationError(
                _('Ensure that %(upper)d comes before %(lower)d'),
                params={'lower': lower, 'upper': upper})
