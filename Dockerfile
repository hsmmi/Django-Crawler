# Use Python base image
FROM python:3.12

# Set the working directory
WORKDIR /app

# Set environment variables
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y postgresql-client

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock ./

# Install dependencies inside virtual environment
RUN poetry config virtualenvs.in-project true

# # Ensure Poetry creates the virtual environment inside /app
# RUN poetry run python -m venv /app/.venv

# Install dependencies inside the container
RUN poetry install --no-root --no-interaction

# Copy the rest of the application code
COPY . .

# Ensure the virtual environment is used
ENV PATH="/app/.venv/bin:$PATH"

# Expose Django port
EXPOSE 8000

# Ensure scripts are executable
RUN chmod +x /app/scripts/start.sh
RUN chmod +x /app/scripts/entrypoint.sh

# Run the entrypoint script
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# CMD ["ls -la /app/.venv/bin"]
# Run the application
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]