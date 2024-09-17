from rest_framework import serializers
from .models import WebApplication, Feature, TestScenario, TestCase


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'name', 'description', 'created_at']


class TestScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestScenario
        fields = ['id', 'scenario_id', 'description', 'purpose', 'created_at']


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = [
            'id', 'test_case_id', 'description', 'pre_conditions', 'test_steps',
            'test_data', 'expected_result', 'post_conditions', 'actual_result',
            'status', 'priority', 'test_environment', 'test_case_type',
            'tester_name', 'date'
        ]


class WebApplicationSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)
    test_scenarios = TestScenarioSerializer(many=True, read_only=True)

    class Meta:
        model = WebApplication
        fields = ['id', 'name', 'url', 'created_at', 'features', 'test_scenarios']
