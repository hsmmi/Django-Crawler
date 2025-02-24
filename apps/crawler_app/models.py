from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="subcategories",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_full_category_path()

    def get_full_category_path(self):
        """Generate full category path e.g., decoration/bedroom/bed"""
        if self.parent:
            return f"{self.parent.get_full_category_path()}/{self.slug}"
        return self.slug


class Product(models.Model):
    """
    Product model

    Parameters:
    - id: int
    - site_id: str
    - title: str
    - original_price: float
    - discount_price: float
    - description: str
    - specifications: dict
    - category: Category
    - url: str
    - images: list[str]
    - availability: bool
    """

    id = models.AutoField(primary_key=True)
    site_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    original_price = models.FloatField()
    discount_price = models.FloatField()
    description = models.TextField(blank=True, null=True)
    specifications = models.JSONField(default=dict)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    url = models.URLField()
    images = models.JSONField()
    availability = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
