from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import TemplateView
from .models import WebApplication, TestScenario, TestCase
from .serializers import WebApplicationSerializer, TestScenarioSerializer, TestCaseSerializer
from .utils import fetch_features_from_url, store_features_in_db
# Create your views here.


class HomePageView(TemplateView):
    template_name = 'index.html'


class WebApplicationCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        url = request.data.get('url')

        if not name or not url:
            return Response({"error": "Name and URL are required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new WebApplication entry
        web_application = WebApplication.objects.create(name=name, url=url)

        # Extract features from the web application
        features = fetch_features_from_url(url)
        store_features_in_db(web_application, features)

        serializer = WebApplicationSerializer(web_application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WebApplicationListAPIView(generics.ListAPIView):
    queryset = WebApplication.objects.all()
    serializer_class = WebApplicationSerializer


class WebApplicationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WebApplication.objects.all()
    serializer_class = WebApplicationSerializer
    lookup_field = 'id'


class TestScenarioListAPIView(generics.ListAPIView):
    queryset = TestScenario.objects.all()
    serializer_class = TestScenarioSerializer


class TestScenarioDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestScenario.objects.all()
    serializer_class = TestScenarioSerializer
    lookup_field = 'id'


class TestCaseListAPIView(generics.ListAPIView):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer


class TestCaseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer
    lookup_field = 'id'
