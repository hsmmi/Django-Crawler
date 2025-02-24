from rest_framework import serializers
from apps.crawler_app.models import Product, Category


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(source="category", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "site_id",
            "title",
            "original_price",
            "discount_price",
            "description",
            "specifications",
            "category_id",
            "category_name",
            "url",
            "images",
            "availability",
            "created_at",
            "updated_at",
        ]


class CategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(source="parent", read_only=True)
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent_id",
            "parent_name",
            "created_at",
            "updated_at",
        ]
