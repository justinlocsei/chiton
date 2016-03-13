from django import forms
from django.utils.translation import ugettext_lazy as _

from chiton.rack.models import AffiliateItem
from chiton.rack.affiliates import create_affiliate
from chiton.rack.affiliates.exceptions import LookupError

api_field_options = {
    'help_text': _('This is automatically populated by the API'),
    'widget': forms.TextInput(attrs={'readonly': True})
}


class AffiliateItemURLForm(forms.ModelForm):
    """A form that fetches additional data on an affiliate item from its URL.

    This requires only the network and URL, and uses those values to request
    more data on the item via the network's API.
    """

    guid = forms.CharField(required=False, label=_('GUID'), **api_field_options)
    name = forms.CharField(required=False, label=_('Name'), **api_field_options)
    url = forms.CharField(required=True, label=_('URL'), widget=forms.URLInput)

    class Meta:
        model = AffiliateItem
        fields = ['network', 'url', 'guid', 'name']

    def clean(self):
        """Get overview data from the affiliate if a URL and network are set."""
        super().clean()

        network = self.cleaned_data.get('network')
        url = self.cleaned_data.get('url')

        if network and url:
            affiliate = create_affiliate(slug=network.slug)

            try:
                response = affiliate.request_overview(url)
            except LookupError as e:
                raise forms.ValidationError(str(e))

            self.cleaned_data['guid'] = response['guid']
            self.cleaned_data['name'] = response['name']
