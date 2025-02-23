# Use Python base image
FROM python:3.12

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock ./

# Install dependencies inside virtual environment
RUN poetry config virtualenvs.create true
RUN poetry install --no-root

# Copy the rest of the application
COPY . .

# Set environment path to use `.venv`
ENV PATH="/app/.venv/bin:$PATH"

# Expose Django port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]