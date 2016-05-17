import time

import mock
import pytest

from chiton.rack.models import AffiliateItem
from chiton.rack.affiliates.bulk import bulk_update_affiliate_item_details, bulk_update_affiliate_item_metadata
from chiton.rack.affiliates.exceptions import ThrottlingError


@pytest.fixture
def affiliate_items(affiliate_network_factory, affiliate_item_factory):
    network = affiliate_network_factory(name='Network')
    for i in range(0, 4):
        affiliate_item_factory(name=str(i), network=network)
    return AffiliateItem.objects.all()


class _TestBulkFunction:

    item_function_path = None

    def items_function(self):
        raise NotImplementedError()

    def test_results(self, affiliate_items):
        """It processes each affiliate item."""
        processed_count = 0
        error_count = 0

        with mock.patch(self.item_function_path) as update_function:
            batch_job = self.items_function(affiliate_items)
            for result in batch_job.run():
                processed_count += 1
                error_count += int(result.is_error)

            assert update_function.call_count == 4
            assert processed_count == 4
            assert error_count == 0

    def test_results_label(self, affiliate_items):
        """It labels each job result with the item's name and network."""
        labels = set()

        with mock.patch(self.item_function_path):
            batch_job = self.items_function(affiliate_items)
            for result in batch_job.run():
                labels.add(result.label)

            assert len(labels) == 4
            for label in labels:
                assert 'Network' in label

    def test_results_errors(self, affiliate_items):
        """It flags whether a result was an error or not."""
        with mock.patch(self.item_function_path) as update_function:
            update_function.side_effect = ValueError()
            batch_job = self.items_function(affiliate_items)

            error_count = 0
            for result in batch_job.run():
                error_count += int(result.is_error)

            assert error_count == 4

    def test_results_error_stacktrace(self, affiliate_items):
        """It includes a stacktrace in the error message."""
        with mock.patch(self.item_function_path) as update_function:
            update_function.side_effect = ValueError('Shopping')
            batch_job = self.items_function(affiliate_items)

            with_message = 0
            for result in batch_job.run():
                with_message += (result.is_error and 'Shopping' in result.details)

            assert with_message == 4

    def test_results_workers(self, affiliate_items):
        """It divides processing across many async workers."""
        with mock.patch(self.item_function_path) as update_function:
            update_function.side_effect = lambda *args, **kwargs: time.sleep(0.1)

            few_workers = self.items_function(affiliate_items, workers=1)
            few_start = time.time()
            for result in few_workers.run():
                pass
            few_end = time.time()

            many_workers = self.items_function(affiliate_items, workers=4)
            many_start = time.time()
            for result in many_workers.run():
                pass
            many_end = time.time()

            few_duration = few_end - few_start
            many_duration = many_end - many_start

            assert many_duration < few_duration

    def test_results_throttling(self, affiliate_items):
        """It retries requests after a delay in response to throttling errors."""
        call_count = 0

        def throttle_initial(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                raise ThrottlingError()

        with mock.patch(self.item_function_path) as update_function:
            with mock.patch('chiton.rack.affiliates.bulk.sleep') as delay_function:
                update_function.side_effect = throttle_initial

                batch_job = self.items_function(affiliate_items)
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
            with mock.patch(self.item_function_path) as update_function:
                with mock.patch('chiton.rack.affiliates.bulk.sleep') as delay_function:
                    update_function.side_effect = ThrottlingError()

                    error_count = 0
                    batch_job = self.items_function(affiliate_items, max_retries=datum['retries'])
                    for result in batch_job.run():
                        error_count += int(result.is_error)

                    assert error_count == 4
                    assert delay_function.call_count == datum['delay_calls']
                    assert update_function.call_count == datum['update_calls']

    def test_results_throttling_jitter(self, affiliate_items):
        """It randomizes the delay between request retries."""
        with mock.patch(self.item_function_path) as update_function:
            with mock.patch('chiton.rack.affiliates.bulk.sleep') as delay_function:
                update_function.side_effect = ThrottlingError()

                batch_job = self.items_function(affiliate_items, max_retries=10)
                for result in batch_job.run():
                    pass

                delay_timings = set()
                for call in delay_function.call_args_list:
                    delay_timings.add(call[0][0])

                assert len(delay_timings) > 1
                assert len(delay_timings) <= delay_function.call_count


@pytest.mark.django_db
class TestBulkUpdateAffiliateItemMetadata(_TestBulkFunction):

    item_function_path = 'chiton.rack.affiliates.bulk.update_affiliate_item_metadata'

    def items_function(self, *args, **kwargs):
        return bulk_update_affiliate_item_metadata(*args, **kwargs)


@pytest.mark.django_db
class TestBulkUpdateAffiliateItemDetails(_TestBulkFunction):

    item_function_path = 'chiton.rack.affiliates.bulk.update_affiliate_item_details'

    def items_function(self, *args, **kwargs):
        return bulk_update_affiliate_item_details(*args, **kwargs)
