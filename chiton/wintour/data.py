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

EXPECTATION_FREQUENCIES = {
    'NEVER': 'never',
    'RARELY': 'rarely',
    'SOMETIMES': 'sometimes',
    'OFTEN': 'often',
    'ALWAYS': 'always'
}

EXPECTATION_FREQUENCY_CHOICES = (
    (EXPECTATION_FREQUENCIES['NEVER'], _('Never')),
    (EXPECTATION_FREQUENCIES['RARELY'], _('Occasionally')),
    (EXPECTATION_FREQUENCIES['SOMETIMES'], _('1-2 times per week')),
    (EXPECTATION_FREQUENCIES['OFTEN'], _('3-4 times per week')),
    (EXPECTATION_FREQUENCIES['ALWAYS'], _('5+ times per week'))
)
