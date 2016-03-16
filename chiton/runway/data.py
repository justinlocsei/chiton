from django.utils.translation import ugettext_lazy as _


PROPRIETY_IMPORTANCES = {
    'MILDLY': 'mildly',
    'SOMEWHAT': 'somewhat',
    'VERY': 'very',
    'ALWAYS': 'always'
}

PROPRIETY_IMPORTANCE_CHOICES = (
    (PROPRIETY_IMPORTANCES['MILDLY'], _('Not that important')),
    (PROPRIETY_IMPORTANCES['SOMEWHAT'], _('Somewhat important')),
    (PROPRIETY_IMPORTANCES['VERY'], _('Very important')),
    (PROPRIETY_IMPORTANCES['ALWAYS'], _('Always important'))
)

PROPRIETY_IMPORTANCE_WEIGHTS = {
    PROPRIETY_IMPORTANCES['MILDLY']: 1,
    PROPRIETY_IMPORTANCES['SOMEWHAT']: 2,
    PROPRIETY_IMPORTANCES['VERY']: 3,
    PROPRIETY_IMPORTANCES['ALWAYS']: 5
}
