from django.utils.translation import ugettext_lazy as _


SLEEVE_LENGTHS = {
    'LONG': 'long',
    'SHORT': 'short',
    'TANK': 'tank',
    'THREE_QUARTER': '3/4'
}

SLEEVE_LENGTH_CHOICES = (
    (SLEEVE_LENGTHS['TANK'], _('Tank')),
    (SLEEVE_LENGTHS['SHORT'], _('Short')),
    (SLEEVE_LENGTHS['THREE_QUARTER'], _('3/4')),
    (SLEEVE_LENGTHS['LONG'], _('Long'))
)

BOTTOM_LENGTHS = {
    'ANKLE': 'ankle',
    'KNEE': 'knee',
    'LONG': 'long',
    'SHORT': 'short',
    'THREE_QUARTER': '3/4'
}

BOTTOM_LENGTH_CHOICES = (
    (BOTTOM_LENGTHS['SHORT'], _('Short')),
    (BOTTOM_LENGTHS['KNEE'], _('Knee')),
    (BOTTOM_LENGTHS['THREE_QUARTER'], _('3/4')),
    (BOTTOM_LENGTHS['ANKLE'], _('Ankle')),
    (BOTTOM_LENGTHS['LONG'], _('Long'))
)
