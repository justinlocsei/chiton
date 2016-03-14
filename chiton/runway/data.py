from django.utils.translation import ugettext_lazy as _


PROPRIETY_WEIGHTS = {
    'RARELY': 1,
    'INFREQUENTLY': 2,
    'FREQUENTLY': 3,
    'ALWAYS': 5
}

PROPRIETY_WEIGHT_CHOICES = (
    (PROPRIETY_WEIGHTS['RARELY'], _('Ever')),
    (PROPRIETY_WEIGHTS['INFREQUENTLY'], _('At least once a week')),
    (PROPRIETY_WEIGHTS['FREQUENTLY'], _('A few days a week')),
    (PROPRIETY_WEIGHTS['ALWAYS'], _('Every day'))
)
