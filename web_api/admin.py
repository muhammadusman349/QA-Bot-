from django.contrib import admin
from .models import WebApplication, Feature, TestScenario, TestCase
# Register your models here.

admin.site.register(WebApplication)
admin.site.register(Feature)
admin.site.register(TestScenario)
admin.site.register(TestCase)
