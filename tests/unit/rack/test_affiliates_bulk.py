from time import sleep

import mock
import pytest

from chiton.rack.models import AffiliateItem
from chiton.rack.affiliates.base import Affiliate
from chiton.rack.affiliates.bulk import BatchJob, bulk_update_affiliate_item_details, bulk_update_affiliate_item_metadata, prune_affiliate_items
from chiton.rack.affiliates.data import update_affiliate_item_details, update_affiliate_item_metadata
from chiton.rack.affiliates.exceptions import BatchError, LookupError, ThrottlingError


class InvalidAffiliate(Affiliate):
    """An affiliate that defines a function to check if an item is invalid."""

    invalid_names = []

    def provide_item_validity(self, item):
        return item.name in self.invalid_names


@pytest.fixture
def affiliate_items(affiliate_item_factory):
    for i in range(0, 4):
        affiliate_item_factory(name=str(i))
    return AffiliateItem.objects.all()


@pytest.fixture
def named_affiliate_items_factory(affiliate_item_factory):
    def factory(names=[]):
        for name in names:
            affiliate_item_factory(name=name)
        return AffiliateItem.objects.all()

    return factory


@pytest.mark.django_db
class TestBatchJob:

    def test_results(self, affiliate_items):
        """It processes each affiliate item."""
        processed_count = 0
        error_count = 0

        updater = mock.Mock()
        batch_job = BatchJob(affiliate_items, updater)

        for result in batch_job.run():
            processed_count += 1
            error_count += int(result.is_error)

        assert updater.call_count == 4
        assert processed_count == 4
        assert error_count == 0

    def test_results_success(self, affiliate_items):
        """It marks all completed jobs as successful."""
        success_count = 0

        updater = mock.Mock()
        batch_job = BatchJob(affiliate_items, updater)

        for result in batch_job.run():
            success_count += int(not result.is_error)

        assert success_count == 4

    def test_results_errors(self, affiliate_items):
        """It flags whether a result was an error or not."""
        updater = mock.Mock(side_effect=ValueError())
        batch_job = BatchJob(affiliate_items, updater)

        error_count = 0
        for result in batch_job.run():
            error_count += int(result.is_error)

        assert error_count == 4

    def test_results_error_stacktrace(self, affiliate_items):
        """It includes a stacktrace in the error message."""
        updater = mock.Mock(side_effect=ValueError('Shopping'))
        batch_job = BatchJob(affiliate_items, updater)

        with_message = 0
        for result in batch_job.run():
            with_message += (result.is_error and 'Shopping' in result.details)

        assert with_message == 4

    def test_results_workers(self, affiliate_items):
        """It allows for a custom worker count to be specified."""
        success_count = 0
        updater = mock.Mock()

        few_workers = BatchJob(affiliate_items, updater, workers=1)
        for result in few_workers.run():
            success_count += int(not result.is_error)

        many_workers = BatchJob(affiliate_items, updater, workers=4)
        for result in many_workers.run():
            success_count += int(not result.is_error)

        assert success_count == 8
        assert updater.call_count == 8

    def test_results_throttling(self, affiliate_items):
        """It retries requests after a delay in response to throttling errors."""
        call_count = 0

        def throttle_initial(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                raise ThrottlingError()

        update_function = mock.Mock(side_effect=throttle_initial)
        batch_job = BatchJob(affiliate_items, update_function)

        with mock.patch('chiton.rack.affiliates.bulk.sleep') as delay_function:
            for result in batch_job.run():
                pass

            assert delay_function.call_count == 3
            assert update_function.call_count == 7

    def test_results_throttling_retries(self, affiliate_items):
        """It retries throttled requests until the retries exceed a maximum value."""
        data = [
            {'retries': 1, 'delay_calls': 4, 'update_calls': 8},
            {'retries': 4, 'delay_calls': 16, 'update_calls': 20}
        ]

        for datum in data:
            update_function = mock.Mock(side_effect=ThrottlingError())

            with mock.patch('chiton.rack.affiliates.bulk.sleep') as delay_function:
                error_count = 0
                batch_job = BatchJob(affiliate_items, update_function, max_retries=datum['retries'])
                for result in batch_job.run():
                    error_count += int(result.is_error)

                assert error_count == 4
                assert delay_function.call_count == datum['delay_calls']
                assert update_function.call_count == datum['update_calls']

    def test_results_throttling_jitter(self, affiliate_items):
        """It randomizes the delay between request retries."""
        update_function = mock.Mock(side_effect=ThrottlingError())

        with mock.patch('chiton.rack.affiliates.bulk.sleep') as delay_function:
            batch_job = BatchJob(affiliate_items, update_function, max_retries=10)
            for result in batch_job.run():
                pass

            delay_timings = set()
            for call in delay_function.call_args_list:
                delay_timings.add(call[0][0])

            assert len(delay_timings) > 1
            assert len(delay_timings) <= delay_function.call_count

    def test_queue_empty(self, affiliate_items):
        """It gracefully handles queue timeout errors."""
        tick = 0

        def throttle(*args, **kwargs):
            nonlocal tick
            sleep(tick * 2)
            tick += 1

        update_function = mock.Mock(side_effect=throttle)
        batch_job = BatchJob(affiliate_items, update_function)

        completed_jobs = 0

        with mock.patch('chiton.rack.affiliates.bulk.QUEUE_TIMEOUT', 1):
            with pytest.raises(BatchError):
                for result in batch_job.run():
                    completed_jobs += 1

        assert completed_jobs == 1

    @pytest.mark.django_db(transaction=True)
    def test_results_lookup_error(self, affiliate_items):
        """It removes items that cause lookup errors."""
        item_pks = affiliate_items.values_list('pk', flat=True)

        def error_first(item):
            if item.name == "0":
                raise LookupError()

        update_function = mock.Mock(side_effect=error_first)
        batch_job = BatchJob(affiliate_items, update_function)

        success_count = 0
        for result in batch_job.run():
            success_count += int(not result.is_error)

        assert success_count == 3

        items = AffiliateItem.objects.filter(pk__in=item_pks)
        assert items.count() == 3


@pytest.mark.django_db
class TestBulkUpdateAffiliateItemMetadata:

    def test_create_batch_job(self, affiliate_items):
        """It creates a batch job that updates metadata."""
        with mock.patch('chiton.rack.affiliates.bulk.BatchJob') as batch_job:
            bulk_update_affiliate_item_metadata(affiliate_items)

            call_args = batch_job.call_args[0]
            assert call_args[0].count() == 4
            assert call_args[1] == update_affiliate_item_metadata

    def test_async_config(self, affiliate_items):
        """It passes the async configuration to the batch job."""
        with mock.patch('chiton.rack.affiliates.bulk.BatchJob') as batch_job:
            bulk_update_affiliate_item_metadata(affiliate_items, workers=10, max_retries=20)

            call_kwargs = batch_job.call_args[1]
            assert call_kwargs['workers'] == 10
            assert call_kwargs['max_retries'] == 20


@pytest.mark.django_db
class TestBulkUpdateAffiliateItemDetails:

    def test_create_batch_job(self, affiliate_items):
        """It creates a batch job that updates details."""
        with mock.patch('chiton.rack.affiliates.bulk.BatchJob') as batch_job:
            bulk_update_affiliate_item_details(affiliate_items)

            call_args = batch_job.call_args[0]
            assert call_args[0].count() == 4
            assert call_args[1] == update_affiliate_item_details

    def test_async_config(self, affiliate_items):
        """It passes the async configuration to the batch job."""
        with mock.patch('chiton.rack.affiliates.bulk.BatchJob') as batch_job:
            bulk_update_affiliate_item_details(affiliate_items, workers=10, max_retries=20)

            call_kwargs = batch_job.call_args[1]
            assert call_kwargs['workers'] == 10
            assert call_kwargs['max_retries'] == 20


@pytest.mark.django_db
class TestPruneAffiliateItems:

    def test_remove_invalid(self, named_affiliate_items_factory):
        """It removes all affiliate items that report themselves as invalid."""
        with mock.patch('chiton.rack.affiliates.bulk.create_affiliate') as create_affiliate:
            affiliate = InvalidAffiliate()
            affiliate.invalid_names = ['one', 'three']
            create_affiliate.return_value = affiliate

            items = named_affiliate_items_factory(['one', 'two', 'three', 'four'])
            assert AffiliateItem.objects.count() == 4

            prune_affiliate_items(items)
            assert sorted([i.name for i in AffiliateItem.objects.all()]) == ['four', 'two']

    def test_removed_count(self, named_affiliate_items_factory):
        """It returns the number of removed items."""
        with mock.patch('chiton.rack.affiliates.bulk.create_affiliate') as create_affiliate:
            affiliate = InvalidAffiliate()
            affiliate.invalid_names = ['one']
            create_affiliate.return_value = affiliate

            items = named_affiliate_items_factory(['one', 'two'])
            pruned = prune_affiliate_items(items)
            assert pruned == 1

    def test_multiple_afiliates(self, affiliate_network_factory, affiliate_item_factory):
        """It uses the appropriate affiliate to check for item validity."""
        def fetch_affiliate(slug=None):
            affiliate = InvalidAffiliate()
            affiliate.invalid_names = [slug]

            return affiliate

        network_one = affiliate_network_factory(slug='one')
        network_two = affiliate_network_factory(slug='two')

        affiliate_item_factory(name='one', network=network_one)
        affiliate_item_factory(name='two', network=network_two)

        valid_one = affiliate_item_factory(name='two', network=network_one)
        valid_two = affiliate_item_factory(name='one', network=network_two)

        with mock.patch('chiton.rack.affiliates.bulk.create_affiliate') as create_affiliate:
            create_affiliate.side_effect = fetch_affiliate

            pruned = prune_affiliate_items(AffiliateItem.objects.all())
            assert pruned == 2

            remaining = set(AffiliateItem.objects.all())
            assert set([valid_one, valid_two]) == remaining
