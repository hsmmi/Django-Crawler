from django import forms
from apps.crawler_app.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "original_price",
            "discount_price",
            "description",
            "specifications",
            "images",
            "category",
            "url",
            "availability",
        ]
