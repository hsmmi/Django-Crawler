import os
from celery import Celery
import django

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django
django.setup()

# Create Celery app instance
app = Celery("django_crawler")

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks in installed apps
app.autodiscover_tasks(
    lambda: [app_config.name for app_config in django.apps.apps.get_app_configs()]
)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
