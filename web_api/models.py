from django.db import models

# Create your models here.


class WebApplication(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Feature(models.Model):
    web_application = models.ForeignKey(WebApplication, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TestScenario(models.Model):
    web_application = models.ForeignKey(WebApplication, on_delete=models.CASCADE, related_name='test_scenarios')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='test_scenarios')
    scenario_id = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    purpose = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.scenario_id


class TestCase(models.Model):
    test_scenario = models.ForeignKey(TestScenario, on_delete=models.CASCADE, related_name='test_cases')
    test_case_id = models.CharField(max_length=100)
    description = models.TextField()
    pre_conditions = models.TextField()
    test_steps = models.TextField()
    test_data = models.TextField(blank=True, null=True)
    expected_result = models.TextField()
    post_conditions = models.TextField(blank=True, null=True)
    actual_result = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('Pass', 'Pass'), ('Fail', 'Fail')], blank=True, null=True)
    priority = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    test_environment = models.CharField(max_length=100)
    test_case_type = models.CharField(max_length=50)
    tester_name = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.test_case_id
