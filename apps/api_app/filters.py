import django_filters
from django.db.models import Q, F
from apps.crawler_app.models import Category, Product


class CategoryFilter(django_filters.FilterSet):
    subcategories = django_filters.CharFilter(method="filter_subcategories")
    parent_slug = django_filters.CharFilter(
        field_name="parent__slug", lookup_expr="iexact"
    )
    slug = django_filters.CharFilter(field_name="slug", lookup_expr="iexact")
    parent_name = django_filters.CharFilter(
        field_name="parent__name", lookup_expr="iexact"
    )
    exact_match = django_filters.BooleanFilter(method="filter_exact_match")

    class Meta:
        model = Category
        fields = [
            "name",
            "slug",
            "parent_slug",
            "parent_name",
            "exact_match",
            "subcategories",
        ]

    def filter_exact_match(self, queryset, name, value):
        """If True, apply exact match filtering for category name."""
        if value:
            return queryset.filter(name=self.data.get("name", ""))
        return queryset

    def filter_subcategories(self, queryset, name, value):
        """Fetches all subcategories when filtering by a parent category."""
        parent_category = Category.objects.filter(slug=value).first()
        if parent_category:
            return queryset.filter(parent=parent_category)
        return queryset.none()


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method="filter_category_with_subcategories")
    min_price = django_filters.NumberFilter(
        field_name="discount_price", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="discount_price", lookup_expr="lte"
    )
    availability = django_filters.BooleanFilter(field_name="availability")
    name = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )
    has_discount = django_filters.BooleanFilter(
        method="filter_has_discount",
        label="Has Discount",
    )
    created_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte"
    )
    updated_after = django_filters.DateFilter(
        field_name="updated_at", lookup_expr="gte"
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "min_price",
            "max_price",
            "availability",
            "name",
            "description",
            "has_discount",
            "created_after",
            "updated_after",
        ]

    def filter_category_with_subcategories(self, queryset, name, value):
        """Include products from selected category and all its subcategories."""
        return queryset.filter(
            Q(category__slug=value)
            | Q(category__parent__slug=value)
            | Q(category__parent__parent__slug=value)
        )

    def filter_has_discount(self, queryset, name, value):
        """Filter products based on whether they have a discount."""
        if value:  # When has_discount=True, filter products with a discount
            return queryset.filter(original_price__gt=F("discount_price"))
        else:  # When has_discount=False, filter products without a discount
            return queryset.filter(original_price=F("discount_price"))
