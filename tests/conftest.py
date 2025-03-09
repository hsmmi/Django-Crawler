"""
conftest.py - Pytest configuration and fixtures for Django testing

This module sets up Django for pytest, configures the test database,
and provides fixtures to manage test execution.

Features:
 - Auto-configures Django settings if not already set.
 - Ensures the test database exists before running tests.
 - Runs migrations to prepare the test environment.
 - Provides a pytest fixture to initialize Django before tests.
"""

import os
import django
import pytest
from django.db import connection
from django.conf import settings
from django.core.management import call_command
from utils.logging import logger


@pytest.fixture(scope="session", autouse=True)
def setup_django(django_db_setup, django_db_blocker):
    """
    Pytest fixture to set up Django for tests.

    - Configures Django settings if not already set.
    - Calls `django.setup()` to initialize Django.
    - Ensures the test database is created and migrated.
    - Runs before all tests (`autouse=True`).

    Logs:
    - Logs when Django settings are configured.
    - Logs when Django setup is completed.
    - Logs when the test environment is ready.
    """

    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    if not settings.configured:
        logger.info("🔄 Configuring Django settings for test session...")
        settings.configure(DJANGO_SETTINGS_MODULE="config.settings")

    django.setup()

    logger.info("🎯 Django is ready for tests!")

    # Ensure the test database exists
    with django_db_blocker.unblock():
        ensure_test_db()


@pytest.fixture(scope="session")
def django_db_setup():
    """
    Pytest fixture to configure the Django test database.

    This fixture is required for pytest-django to allow database access.
    It ensures that tests can interact with the database.
    """
    pass  # This enables the DB for the session


def ensure_test_db():
    """
    Ensures the test database is created and ready before running tests.

    - Checks if the test database exists.
    - Creates the test database if it does not exist.
    - Runs Django migrations to prepare the schema.

    Logs:
    - Test database name.
    - Whether the test database was created or already exists.
    - Status of database migrations.
    """
    test_db_name = settings.DATABASES["default"]["TEST"]["NAME"]
    settings.DATABASES["default"]["NAME"] = test_db_name
    logger.info(f"🔍 Test DB Name: {test_db_name}")

    logger.info(f"⚡ Ensuring test database `{test_db_name}` exists...")

    # Use a raw connection to PostgreSQL to check/create the database
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    conn = psycopg2.connect(
        dbname="postgres",
        user=settings.DATABASES["default"]["USER"],
        password=settings.DATABASES["default"]["PASSWORD"],
        host=settings.DATABASES["default"]["HOST"],
        port=settings.DATABASES["default"]["PORT"],
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{test_db_name}'")
    exists = cursor.fetchone()

    if exists:
        logger.info("✅ Test DB already exists, skipping creation.")
    else:
        logger.info("🛠 Creating test DB manually...")
        cursor.execute(
            f"CREATE DATABASE {test_db_name} OWNER {settings.DATABASES['default']['USER']}"
        )

    cursor.close()
    conn.close()

    logger.info("🚀 Running migrations for the test DB...")
    call_command("migrate")

    logger.info("✅ Test DB is ready.")
