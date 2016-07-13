import mock
import pytest

from chiton.rack.affiliates.exceptions import LookupError
from chiton.rack.affiliates.responses import ItemOverview
from chiton.rack.forms import AffiliateItemURLForm


@pytest.mark.django_db
class TestAffiliateItemURLForm:

    def test_empty(self):
        """It does not set the GUID or name when no network or URL is selected."""
        form = AffiliateItemURLForm({})

        assert form.is_valid() is False
        assert not form.cleaned_data['guid']
        assert not form.cleaned_data['name']

    def test_unset(self):
        """It does not unset the GUID or name if a network or URL is not chosen."""
        form = AffiliateItemURLForm({'guid': 'guid', 'name': 'name'})

        assert form.is_valid() is False
        assert form.cleaned_data['guid'] == 'guid'
        assert form.cleaned_data['name'] == 'name'

    def test_network_url(self, garment_factory, affiliate_network_factory):
        """It fetches the name and GUID from an affiliate when a network and URL are provided."""
        garment = garment_factory()
        network = affiliate_network_factory(slug='test_affiliate')

        form = AffiliateItemURLForm({
            'garment': garment.pk,
            'network': network.pk,
            'url': 'http://example.com',
            'retailer': 'Amazon'
        })

        with mock.patch('chiton.rack.forms.create_affiliate') as create_affiliate:
            affiliate = mock.MagicMock()
            affiliate.request_overview = mock.MagicMock()
            affiliate.request_overview.return_value = ItemOverview({'guid': 'guid', 'name': 'name'})
            create_affiliate.return_value = affiliate

            assert form.is_valid()
            create_affiliate.assert_called_with(slug='test_affiliate')
            affiliate.request_overview.assert_called_with('http://example.com')

        assert form.cleaned_data['name'] == 'name'
        assert form.cleaned_data['guid'] == 'guid'

    def test_affiliate_errors(self, garment_factory, affiliate_network_factory):
        """It raises affiliate lookup errors as validation errors."""
        garment = garment_factory()
        network = affiliate_network_factory(slug='test_affiliate')

        form = AffiliateItemURLForm({
            'garment': garment.pk,
            'network': network.pk,
            'url': 'http://example.com'
        })

        with mock.patch('chiton.rack.forms.create_affiliate') as create_affiliate:
            affiliate = mock.MagicMock()
            affiliate.request_overview = mock.MagicMock(side_effect=LookupError('Invalid lookup'))
            create_affiliate.return_value = affiliate

            assert not form.is_valid()
            assert 'Invalid lookup' in form.non_field_errors()

        assert not form.cleaned_data['name']
        assert not form.cleaned_data['guid']
