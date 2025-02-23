#!/bin/bash
# Apply database migrations
echo "Applying database migrations..."
poetry run python manage.py migrate

# Start Django application
echo "Starting Django application..."
exec "$@"