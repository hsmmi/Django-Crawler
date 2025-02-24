from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, CategoryDetailView

# Initialize router
router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("api/", include(router.urls)),  # Register all router-based viewsets
    path(
        "api/categories/<slug:slug>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
]
