import django_filters
from apps.crawler_app.models import Category, Product


class CategoryFilter(django_filters.FilterSet):
    parent_slug = django_filters.CharFilter(
        field_name="parent__slug", lookup_expr="iexact"
    )
    slug = django_filters.CharFilter(field_name="slug", lookup_expr="iexact")

    class Meta:
        model = Category
        fields = ["name", "slug", "parent_slug"]


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__slug", lookup_expr="iexact"
    )
    min_price = django_filters.NumberFilter(
        field_name="discount_price", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="discount_price", lookup_expr="lte"
    )

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price", "availability"]
