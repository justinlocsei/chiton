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

EMPHASES = {
    'WEAK': -1,
    'NEUTRAL': 0,
    'STRONG': 1
}

EMPHASIS_DISPLAY = {
    EMPHASES['WEAK']: _('Weak'),
    EMPHASES['NEUTRAL']: _('Neutral'),
    EMPHASES['STRONG']: _('Strong')
}

EMPHASIS_CHOICES = (
    (EMPHASES['WEAK'], EMPHASIS_DISPLAY[EMPHASES['WEAK']]),
    (EMPHASES['NEUTRAL'], EMPHASIS_DISPLAY[EMPHASES['NEUTRAL']]),
    (EMPHASES['STRONG'], EMPHASIS_DISPLAY[EMPHASES['STRONG']])
)

PANT_RISES = {
    'LOW': 'low',
    'NORMAL': 'normal',
    'HIGH': 'high'
}

PANT_RISE_CHOICES = (
    (PANT_RISES['LOW'], _('Low')),
    (PANT_RISES['NORMAL'], _('Normal')),
    (PANT_RISES['HIGH'], _('High'))
)

CARE_TYPES = {
    'MACHINE_MACHINE': 'machine_machine',
    'MACHINE_AIR': 'machine_air',
    'HAND_WASH': 'hand_wash',
    'DRY_CLEAN': 'dry_clean'
}

CARE_CHOICES = (
    (CARE_TYPES['MACHINE_MACHINE'], _('Machine wash and dry')),
    (CARE_TYPES['MACHINE_AIR'], _('Machine wash, air dry')),
    (CARE_TYPES['HAND_WASH'], _('Hand wash')),
    (CARE_TYPES['DRY_CLEAN'], _('Dry clean'))
)
