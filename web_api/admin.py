from django.contrib import admin
from .models import WebApplication, Feature, TestScenario, TestCase
# Register your models here.


class WebApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url', 'created_at')
    search_fields = ('id', 'name', 'url')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


admin.site.register(WebApplication, WebApplicationAdmin)
admin.site.register(Feature)
admin.site.register(TestScenario)
admin.site.register(TestCase)
