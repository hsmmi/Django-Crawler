Here’s your updated README with Celery integration added seamlessly.

Django Web Crawler with Docker

This project is a Django-based web crawler that uses PostgreSQL, containerized with Docker and secured using Docker Secrets.

📌 Table of Contents
	•	🚀 Setup Instructions
	•	⚙️ Celery & Task Scheduling
	•	🏷️ Category Structure
	•	⚡ Performance Optimizations
	•	📜 API Documentation
	•	API Endpoints (Router-based)
	•	HTML-Based Views (Template Views)
	•	📊 Logging & Debugging

🚀 Setup Instructions

1️⃣ Initialize Docker Swarm

Before using Docker Secrets, initialize Swarm mode (required for secrets):

docker swarm init

2️⃣ Create Database Secrets

Run the following commands to securely store database credentials:

echo "$DATABASE_NAME" | docker secret create db_name -
echo "$DATABASE_USER" | docker secret create db_user -
echo "$DATABASE_PASSWORD" | docker secret create db_password -
echo "$DATABASE_HOST" | docker secret create db_host -
echo "$DATABASE_PORT" | docker secret create db_port -

To verify the secrets:

docker secret ls

3️⃣ Manually Build the Docker Image

Docker Swarm does not support build: in docker-compose.yml, so you need to build the image manually.

docker build -t django-crawler .

4️⃣ Deploy the Application

Run the following command to start Django, PostgreSQL, Redis, and Celery using Docker Swarm:

docker stack deploy -c docker-compose.yml django-crawler

5️⃣ Managing the Database

Run database migrations inside the container:

docker exec -it $(docker ps -q --filter name=web) poetry run python manage.py migrate

Create database migrations:

docker exec -it $(docker ps -q --filter name=web) poetry run python manage.py makemigrations

Create a superuser for Django Admin:

docker exec -it $(docker ps -q --filter name=web) poetry run python manage.py createsuperuser

6️⃣ Verify the Running Containers

Check that all services are running:

docker ps

Expected output:

CONTAINER ID   IMAGE              STATUS         PORTS
123abc456def   django-crawler     Up 2 minutes   0.0.0.0:8000->8000/tcp
789xyz123ghi   postgres:16        Up 2 minutes   0.0.0.0:5432->5432/tcp
456def789xyz   redis:latest       Up 2 minutes   0.0.0.0:6379->6379/tcp

7️⃣ How to Stop the Application

To stop and remove all services:

docker stack rm django-crawler

To remove unused volumes and networks:

docker system prune -a

⚙️ Celery & Task Scheduling

1️⃣ Install Redis (Required for Celery)

Ensure that Redis is installed and running.

For macOS (Homebrew)

brew install redis
brew services start redis

For Linux (Debian/Ubuntu)

sudo apt update && sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

For Windows (via WSL)

Use Docker or WSL to run Redis:

docker run -d --name redis -p 6379:6379 redis

2️⃣ Start Celery Worker

Run the following command to start a Celery worker:

poetry run celery -A config worker --loglevel=info

This starts Celery in worker mode, listening for tasks.

3️⃣ Running Celery Beat (Scheduled Tasks)

To schedule recurring tasks (e.g., automatic scraping), start Celery Beat:

poetry run celery -A config beat --loglevel=info

4️⃣ Verify Celery is Running

Check active tasks:

poetry run celery -A config inspect active
poetry run celery -A config inspect scheduled
poetry run celery -A config inspect reserved

If no tasks are scheduled, recheck Redis:

redis-cli ping  # Should return PONG

5️⃣ Manually Trigger Web Scraping

To manually test the scraper, enter Django shell:

poetry run python manage.py shell

Then run:

from apps.crawler_app.tasks import scrape_products
scrape_products.delay()

Check Celery logs for execution.

6️⃣ Dockerizing Celery (For Production)

Ensure Celery is running inside Docker for deployments:
	1.	Build the Celery image manually:

docker build -t django-crawler-celery .


	2.	Deploy it as a stack:

docker stack deploy -c docker-compose.yml django-crawler


	3.	Verify services:

docker service ls

✅ Celery in Django Admin
	1.	Open Django Admin (/admin/django_celery_beat/periodictask/)
	2.	Add a new periodic task:
	•	Task Name: scrape_products
	•	Interval: Choose Every X minutes
	3.	Save and start scheduling tasks automatically.

🏷️ Category Structure
	•	Categories are now hierarchical, supporting unlimited depth (e.g., decoration > bedroom > bed).
	•	The system automatically creates missing parent categories when a new category is added.

Example:

Category Path	Parent
decoration > bedroom > bed	decoration > bedroom
office-furniture > table > conference-table	office-furniture > table

# Fetch all categories via API
curl -X GET http://localhost:8000/api/categories/

📜 API Documentation

API Endpoints (Router-based)

These are registered with Django REST framework’s DefaultRouter, meaning they provide CRUD operations automatically.

Endpoint	ViewSet	Description
/api/products/	ProductViewSet	List and manage products (CRUD)
/api/categories/	CategoryViewSet	List and manage categories (CRUD)

📊 Logging & Debugging

Logs are stored in logs/ and can be accessed via:

# View the latest logs
tail -f logs/django.log

# View the latest warnings and errors only
tail -f logs/django_warn.log

This helps debugging and makes log access clear.

🎯 Next Steps

Would you like to:
	•	Optimize query indexing for PostgreSQL?
	•	Implement caching with Redis to speed up repeated queries?
	•	Improve API response times using Django REST Framework optimizations?
	•	Add automated testing with Pytest and FactoryBoy?

✅ Celery is now fully documented in your README! 🎉
🔹 Next up: Writing automated tests. Would you like to begin with unit tests or integration tests? 🚀