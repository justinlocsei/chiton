from django.utils.translation import ugettext_lazy as _


PROPRIETY_IMPORTANCES = {
    'NOT': 'not',
    'MILDLY': 'mildly',
    'SOMEWHAT': 'somewhat',
    'VERY': 'very',
    'ALWAYS': 'always'
}

PROPRIETY_IMPORTANCE_CHOICES = (
    (PROPRIETY_IMPORTANCES['NOT'], _('Not important')),
    (PROPRIETY_IMPORTANCES['MILDLY'], _('Not that important')),
    (PROPRIETY_IMPORTANCES['SOMEWHAT'], _('Somewhat important')),
    (PROPRIETY_IMPORTANCES['VERY'], _('Very important')),
    (PROPRIETY_IMPORTANCES['ALWAYS'], _('Always important'))
)
