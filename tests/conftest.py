import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.crawler_app.models import Product, Category


@pytest.fixture
def api_client():
    """Fixture to provide a DRF API client."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Fixture to create a user in the database."""

    def make_user(**kwargs):
        return User.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def create_category(db):
    """Fixture to create a category in the database."""

    def make_category(name="Test Category", parent=None):
        return Category.objects.create(name=name, parent=parent)

    return make_category


@pytest.fixture
def create_product(db):
    """Fixture to create a product in the database."""

    def make_product(name="Test Product", category=None):
        return Product.objects.create(name=name, category=category)

    return make_product
