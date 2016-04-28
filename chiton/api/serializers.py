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
    formalities = FormalityExpectationSerializer(source='formalityexpectation_set', many=True)

    class Meta:
        model = WardrobeProfile
        fields = ('age', 'formalities', 'shape', 'styles')

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
        """Associate styles and formalities with the profile after creation."""
        formalities = data.pop('formalityexpectation_set')
        styles = data.pop('styles')

        profile = WardrobeProfile.objects.create(**data)
        profile.styles.add(*styles)

        for formality in formalities:
            formality['profile'] = profile
            FormalityExpectation.objects.create(**formality)

        return profile
