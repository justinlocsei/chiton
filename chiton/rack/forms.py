from django import forms
from django.utils.translation import ugettext_lazy as _

from chiton.rack.models import AffiliateItem
from chiton.rack.affiliates import create_affiliate
from chiton.rack.affiliates.exceptions import LookupError


class AffiliateItemURLForm(forms.ModelForm):
    """A form that fetches additional data on an affiliate item from its URL.

    This requires only the network and URL, and uses those values to request
    more data on the item via the network's API.
    """

    _API_FIELD_OPTIONS = {
        'help_text': _('This is automatically populated by the API'),
        'widget': forms.TextInput(attrs={'readonly': True})
    }

    guid = forms.CharField(required=False, label=_('GUID'), **_API_FIELD_OPTIONS)
    name = forms.CharField(required=False, label=_('Name'), **_API_FIELD_OPTIONS)
    price = forms.CharField(required=False, label=_('Price'), **_API_FIELD_OPTIONS)
    url = forms.CharField(required=True, label=_('URL'), widget=forms.URLInput)

    class Meta:
        model = AffiliateItem
        fields = ['garment', 'network', 'url', 'guid', 'name', 'price']

    def clean(self):
        """Get overview data from the affiliate if a URL and network are set."""
        if not self.cleaned_data.get('price'):
            self.cleaned_data.pop('price')

        super().clean()

        network = self.cleaned_data.get('network')
        url = self.cleaned_data.get('url')

        if network and url:
            affiliate = create_affiliate(slug=network.slug)

            try:
                response = affiliate.request_overview(url)
            except LookupError as e:
                raise forms.ValidationError(str(e))

            self.cleaned_data['guid'] = response.guid
            self.cleaned_data['name'] = response.name
