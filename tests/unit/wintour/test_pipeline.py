import pytest

from chiton.closet.models import Garment
from chiton.wintour.pipeline import PipelineStep


class TestStep(PipelineStep):
    name = 'Test'
    slug = 'test'


class TestPipelineStep:

    def test_requires_name(self):
        """It requires subclasses to define a name."""
        class Step(PipelineStep):
            name = None
            slug = 'slug'

        with pytest.raises(NotImplementedError):
            Step()

    def test_requires_slug(self):
        """It requires subclasses to define a slug."""
        class Step(PipelineStep):
            name = 'name'
            slug = None

        with pytest.raises(NotImplementedError):
            Step()

    def test_configure_kwargs(self):
        """It passes initialization kwargs to subclasses."""
        class Step(TestStep):

            def configure(self, key=None):
                self.key = key

        step = Step(key='value')
        assert step.key == 'value'

    def test_logging(self):
        """It allows messages to be logged and retrieved."""
        step = TestStep()

        step.log('root', 'first')
        step.log('root', 'second')

        assert step.get_log_messages('root') == ['first', 'second']

    def test_logging_deep(self):
        """It supports nested log levels."""
        step = TestStep()

        step.log('root', 'first')
        step.log('root.child', 'second')

        assert step.get_log_messages('root') == ['first']
        assert step.get_log_messages('root.child') == ['second']

    def test_logging_empty(self):
        """It returns an empty list for undefined log keys."""
        step = TestStep()

        assert step.get_log_messages('undefined') == []

    @pytest.mark.django_db
    def test_prepare_garments(self, garment_factory):
        """It returns an unmodified garment queryset by default."""
        garment_factory()
        garment_factory()

        step = TestStep()

        garments = Garment.objects.all()
        prepared = step.prepare_garments(garments)

        assert garments.count() == 2
        assert prepared.count() == 2

    def test_apply_to_profile(self, pipeline_profile_factory):
        """It acts as a context manager that provides a function to apply the step to an object."""
        class Step(TestStep):

            def provide_profile_data(self, profile):
                return {
                    'age': profile['age'],
                    'multiplier': 2
                }

            def apply(self, unit, age=None, multiplier=None):
                return '%d %s' % (age * multiplier, unit)

        profile = pipeline_profile_factory(age=10)
        step = Step()

        with step.apply_to_profile(profile) as apply_fn:
            result = apply_fn('years')

            assert result == '20 years'

    def test_apply_to_profile_memoized(self, pipeline_profile_factory):
        """It memoizes the profile data within the application context."""
        class Step(TestStep):

            def configure(self):
                self.counter = 0

            def provide_profile_data(self, profile):
                self.counter += 1
                return {
                    'counter': self.counter
                }

            def apply(self, counter):
                return counter

        profile = pipeline_profile_factory()
        step = Step()

        with step.apply_to_profile(profile) as first_apply:
            first_result = first_apply()
            second_result = first_apply()

            assert first_result == 1
            assert second_result == 1

        with step.apply_to_profile(profile) as second_apply:
            third_result = second_apply()

            assert third_result == 2

    def test_apply_to_profile_empty(self, pipeline_profile_factory):
        """It raises an error when a step does not define its application."""
        profile = pipeline_profile_factory()
        step = TestStep()

        with pytest.raises(NotImplementedError):
            with step.apply_to_profile(profile) as apply_fn:
                apply_fn()
