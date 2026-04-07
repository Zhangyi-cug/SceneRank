from rest_framework import serializers
from .models import SurveyConfig, ComparisonResult


class SurveyConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyConfig
        fields = ['id', 'data', 'updated_at']


class ComparisonResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComparisonResult
        fields = ['id', 'image_a', 'image_b', 'selections', 'background', 'timestamp', 'created_at']
