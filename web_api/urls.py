from django.urls import path
from .views import (
                    HomePageView,
                    WebApplicationCreateAPIView,
                    WebApplicationListAPIView,
                    WebApplicationDetailAPIView,
                    TestScenarioListAPIView,
                    TestScenarioDetailAPIView,
                    TestCaseListAPIView,
                    TestCaseDetailAPIView,
                    )

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('api/web-applications/', WebApplicationCreateAPIView.as_view(), name='web-application-create'),
    path('api/web-applications/list/', WebApplicationListAPIView.as_view(), name='web-application-list'),
    path('api/web-applications/<int:id>/', WebApplicationDetailAPIView.as_view(), name='web-application-detail'),
    # TestScenario URLs
    path('test_scenarios/', TestScenarioListAPIView.as_view(), name='test-scenario-list'),
    path('test_scenarios/<int:id>/', TestScenarioDetailAPIView.as_view(), name='test-scenario-detail'),
    # TestCase URLs
    path('test_cases/', TestCaseListAPIView.as_view(), name='test-case-list'),
    path('test_cases/<int:id>/', TestCaseDetailAPIView.as_view(), name='test-case-detail'),
]
