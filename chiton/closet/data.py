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

SIZES = {
    'XXS': 'xxs',
    'XS': 'xs',
    'S': 's',
    'M': 'm',
    'L': 'l',
    'XL': 'xl',
    'XXL': 'xxl',
    'PLUS_1X': 'plus1',
    'PLUS_2X': 'plus2',
    'PLUS_3X': 'plus3',
    'PLUS_4X': 'plus4',
    'PLUS_5X': 'plus5'
}

SIZE_DISPLAY = {
    SIZES['XXS']: 'XXS',
    SIZES['XS']: 'XS',
    SIZES['S']: 'S',
    SIZES['M']: 'M',
    SIZES['L']: 'L',
    SIZES['XL']: 'XL',
    SIZES['XXL']: 'XXL',
    SIZES['PLUS_1X']: 'Plus 1X',
    SIZES['PLUS_2X']: 'Plus 2X',
    SIZES['PLUS_3X']: 'Plus 3X',
    SIZES['PLUS_4X']: 'Plus 4X',
    SIZES['PLUS_5X']: 'Plus 5X'
}

SIZE_CHOICES = (
    (SIZES['XXS'], SIZE_DISPLAY[SIZES['XXS']]),
    (SIZES['XS'], SIZE_DISPLAY[SIZES['XS']]),
    (SIZES['S'], SIZE_DISPLAY[SIZES['S']]),
    (SIZES['M'], SIZE_DISPLAY[SIZES['M']]),
    (SIZES['L'], SIZE_DISPLAY[SIZES['L']]),
    (SIZES['XL'], SIZE_DISPLAY[SIZES['XL']]),
    (SIZES['XXL'], SIZE_DISPLAY[SIZES['XXL']]),
    (SIZES['PLUS_1X'], SIZE_DISPLAY[SIZES['PLUS_1X']]),
    (SIZES['PLUS_2X'], SIZE_DISPLAY[SIZES['PLUS_2X']]),
    (SIZES['PLUS_3X'], SIZE_DISPLAY[SIZES['PLUS_3X']]),
    (SIZES['PLUS_4X'], SIZE_DISPLAY[SIZES['PLUS_4X']]),
    (SIZES['PLUS_5X'], SIZE_DISPLAY[SIZES['PLUS_5X']])
)
