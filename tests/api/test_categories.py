import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from utils.logging import logger


@pytest.fixture
def api_client():
    """Fixture to provide an API client for tests."""
    return APIClient()


@pytest.mark.django_db
def test_get_categories(api_client):
    """
    Test retrieving the list of categories.

    - Sends a GET request to `/api/categories/`
    - Logs the request and response status
    - Asserts that the response status is 200 (OK)
    - Logs the response JSON
    - Asserts that the response contains an empty list (if no categories exist)
    """
    import django
    from django.db import connection

    print("🔥 Active Database:", connection.settings_dict["NAME"])
    url = reverse("category-list")  # Uses Django's reverse() to get URL
    logger.info(f"🔍 Sending GET request to {url}...")

    response = api_client.get(url)
    logger.info(f"✅ Response Status Code: {response.status_code}")
    logger.info(f"📄 Response JSON: {response.json()}")

    assert response.status_code == 200, "Expected status code 200 for category API"
    assert response.json()["count"] == 0, "Expected count to be 0"
    assert response.json()["results"] == [], "Expected results to be empty"

    logger.info("🎯 Test Passed: Categories API returns expected response!")
