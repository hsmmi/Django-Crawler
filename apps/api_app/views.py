from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from apps.crawler_app.models import Category, Product
from apps.api_app.serializers import CategorySerializer, ProductSerializer
from apps.api_app.filters import CategoryFilter, ProductFilter
from rest_framework.generics import RetrieveAPIView


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter  # Use the filter class


class CategoryDetailView(RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter  # Use the filter class
