from django.urls import path
from apps.api_app.views import (
    product_detail,
    EditProductView,
    DeleteProductView,
    AddProductView,
    product_list,
)

urlpatterns = [
    path("product/", product_list, name="product_list"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),
    path("product/edit/<int:pk>/", EditProductView.as_view(), name="edit_product"),
    path(
        "product/delete/<int:pk>/",
        DeleteProductView.as_view(),
        name="delete_product",
    ),
    path("product/add/", AddProductView.as_view(), name="add_product"),
]
