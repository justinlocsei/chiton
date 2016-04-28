from django.utils.translation import ugettext_lazy as _


BODY_SHAPES = {
    'APPLE': 'apple',
    'HOURGLASS': 'hourglass',
    'INVERTED_TRIANGLE': 'inverted',
    'PEAR': 'pear',
    'RECTANGLE': 'rectangle'
}

BODY_SHAPE_CHOICES = (
    (BODY_SHAPES['PEAR'], _('Pear')),
    (BODY_SHAPES['HOURGLASS'], _('Hourglass')),
    (BODY_SHAPES['INVERTED_TRIANGLE'], _('Inverted triangle')),
    (BODY_SHAPES['APPLE'], _('Apple')),
    (BODY_SHAPES['RECTANGLE'], _('Rectangle'))
)

FORMALITY_FREQUENCIES = {
    'NEVER': 'never',
    'RARELY': 'rarely',
    'SOMETIMES': 'sometimes',
    'OFTEN': 'often',
    'ALWAYS': 'always'
}

FORMALITY_FREQUENCY_CHOICES = (
    (FORMALITY_FREQUENCIES['NEVER'], _('Never')),
    (FORMALITY_FREQUENCIES['RARELY'], _('Occasionally')),
    (FORMALITY_FREQUENCIES['SOMETIMES'], _('1-2 times per week')),
    (FORMALITY_FREQUENCIES['OFTEN'], _('3-4 times per week')),
    (FORMALITY_FREQUENCIES['ALWAYS'], _('5+ times per week'))
)
