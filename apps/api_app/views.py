from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from apps.crawler_app.models import Category, Product
from apps.api_app.serializers import CategorySerializer, ProductSerializer
from apps.api_app.filters import CategoryFilter, ProductFilter
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import render, get_object_or_404
from django.views.generic import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from apps.api_app.forms import ProductForm


class CategoryDetailView(RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})


def product_list(request):
    """Display all products in a simple HTML page."""
    products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})


class EditProductView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "edit_product.html"
    success_url = reverse_lazy("product_list")


class DeleteProductView(DeleteView):
    model = Product
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("product_list")


class AddProductView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "add_product.html"
    success_url = reverse_lazy("product_list")
