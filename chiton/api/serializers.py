from rest_framework import serializers

from chiton.runway.models import Formality, Style
from chiton.wintour.models import FormalityExpectation, WardrobeProfile

class FormalityExpectationSerializer(serializers.ModelSerializer):
    formality = serializers.SlugRelatedField(slug_field='slug', queryset=Formality.objects.all())

    class Meta:
        model = FormalityExpectation
        fields = ('formality', 'frequency')


class WardrobeProfileSerializer(serializers.ModelSerializer):
    styles = serializers.SlugRelatedField(slug_field='slug', many=True, queryset=Style.objects.all())
    expectations = FormalityExpectationSerializer(many=True)

    class Meta:
        model = WardrobeProfile
        fields = ('age', 'expectations', 'shape', 'styles')

    def validate_styles(self, value):
        """Ensure that at least one style is provided."""
        if not len(value):
            raise serializers.ValidationError('At least one style must be provided')
        return value

    def validate_formalities(self, value):
        """Ensure that at least one formality expectation is provided."""
        if not len(value):
            raise serializers.ValidationError('At least one formality expectation must be provided')
        return value

    def create(self, data):
        """Associate styles and formality expectations with the profile after creation."""
        expectations = data.pop('expectations')
        styles = data.pop('styles')

        profile = WardrobeProfile.objects.create(**data)
        profile.styles.add(*styles)

        for expectation in expectations:
            expectation['profile'] = profile
            FormalityExpectation.objects.create(**expectation)

        return profile
