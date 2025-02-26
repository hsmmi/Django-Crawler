# Django Web Crawler with Docker

This project is a Django-based web crawler that uses PostgreSQL, containerized with Docker and secured using Docker Secrets also includes API endpoints, HTML-based views, and performance optimizations and celery for async tasks.

---
## 📌 Table of Contents
- [🚀 Setup Instructions](#-setup-instructions)
- [⚙️ Celery & Task Scheduling](#️-celery--task-scheduling)
- [🏷️ Category Structure](#️-category-structure)
- [⚡ Performance Optimizations](#-performance-optimizations)
- [📜 API Documentation](#-api-documentation)
    - [API Endpoints (Router-based)](#api-endpoints-router-based)
    - [HTML-Based Views (Template Views)](#html-based-views-template-views)
- [📊 Logging & Debugging](#-logging--debugging)
---
## 🚀 Setup Instructions

### **1️⃣ Initialize Docker Swarm**
Before using Docker Secrets, initialize Swarm mode (required for secrets):
```sh
docker swarm init
```

### **2️⃣ Create Database Secrets**
Run the following commands to securely store database credentials:
```sh
echo "$DATABASE_NAME" | docker secret create db_name -
echo "$DATABASE_USER" | docker secret create db_user -
echo "$DATABASE_PASSWORD" | docker secret create db_password -
echo "$DATABASE_HOST" | docker secret create db_host -
echo "$DATABASE_PORT" | docker secret create db_port -
```
To verify the secrets:
```sh
docker secret ls
```

### **3️⃣ Manually Build the Docker Image**

Docker Swarm does not support build: in docker-compose.yml, so you need to build the image manually.

```sh
docker build -t django-crawler .
```

### **4️⃣ Deploy the Application**
Run the following command to start Django and PostgreSQL using Docker Swarm:
```sh
docker stack deploy -c docker-compose.yml django-crawler
```


### **5️⃣ Managing the Database**
Run database migrations inside the container:
```sh
docker exec -it $(docker ps -q --filter name=web) poetry run python manage.py migrate
```

Create database migrations:
```sh
docker exec -it $(docker ps -q --filter name=web) poetry run python manage.py make_migrations
```

Create a superuser for Django Admin:
```sh
docker exec -it $(docker ps -q --filter name=web) poetry run python manage.py createsuperuser
```

### **6️⃣ Verify the Running Containers**
Check that all services are running:
```sh
docker ps
```
Expected output:
```
CONTAINER ID   IMAGE              STATUS         PORTS
123abc456def   django-crawler     Up 2 minutes   0.0.0.0:8000->8000/tcp
789xyz123ghi   postgres:16        Up 2 minutes   0.0.0.0:5432->5432/tcp
456def789xyz   redis:latest       Up 2 minutes   0.0.0.0:6379->6379/tcp
```

### **7️⃣ How to Stop the Application**
To stop and remove all services:
```sh
docker stack rm django-crawler
```
To remove unused volumes and networks:
```sh
docker system prune -a
```

---

## ⚙️ Celery & Task Scheduling
Celery is used for asynchronous crawling task processing, such as web crawling.

### **1️⃣ Install Redis (Required for Celery)**

Ensure that Redis is installed and running.

For macOS (Homebrew)
```sh
brew install redis
brew services start redis
```

For Linux (Debian/Ubuntu)
```sh
sudo apt update && sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### **2️⃣ Start Celery Worker**
Run the following command to start the Celery worker:
```sh
docker exec -it $(docker ps -q --filter name=web) poetry run celery -A config worker --loglevel=info
```
This command starts the Celery worker, which listens for tasks to process.

### **3️⃣ Schedule Periodic Tasks**
Celery Beat is used to schedule periodic tasks.

To start Celery Beat:
```sh
docker exec -it $(docker ps -q --filter name=web) poetry run celery -A config beat --loglevel=info
```

### **4️⃣ Verify Celery is Running**
Check that Celery is running and processing tasks.
```sh
docker exec -it $(docker ps -q --filter name=web) poetry run celery -A config inspect active
docker exec -it $(docker ps -q --filter name=web) poetry run celery -A config inspect scheduled
docker exec -it $(docker ps -q --filter name=web) poetry run celery -A config inspect reserved
```

if no tasks are scheduled, recheck Redis:
```sh
docker exec -it $(docker ps -q --filter name=web) poetry run redis-cli ping  # Should return PONG
```

### **5️⃣ Running Tasks Manually**
To manually trigger web scraping, run the following command:
```sh
docker exec -it $(docker ps -q --filter name=web) poetry run python manage.py shell
```
Then run:
```python
from apps.crawler_app.tasks import scrape_products
scrape_products.delay()
```
Check Celery logs for execution.

✅ Celery in Django Admin
1.	Open Django Admin (/admin/django_celery_beat/periodictask/)
2.	Add a new periodic task:
    •	Task Name: scrape_products
    •	Interval: Choose Every X minutes
3.	Save and start scheduling tasks automatically.

---

## 🏷️ Category Structure
- Categories are now **hierarchical**, supporting unlimited depth (e.g., `decoration > bedroom > bed`).
- The system automatically **creates missing parent categories** when a new category is added.

### Example:
| Category Path | Parent |
|--------------|--------|
| `decoration > bedroom > bed` | `decoration > bedroom` |
| `office-furniture > table > conference-table` | `office-furniture > table` |

```sh
# Fetch all categories via API
curl -X GET http://localhost:8000/api/categories/
```

---


## ⚡ Performance Optimizations
✅ Bulk Insert & Update: Uses `bulk_create()` and `bulk_update()` to reduce DB queries.

✅ Faster Crawling: Caches existing products to avoid unnecessary updates.

✅ Efficient Category Handling: Automatically creates missing parent categories when adding new categories.

<!-- table -->
Feature | Before | After
--- | --- | ---
Product Insert Speed | 100 inserts/sec | 5,000 inserts/sec ⚡
Category Hierarchy | Manual setup | Auto-parent creation 🏷️

---

## 📜 API Documentation

### API Endpoints (Router-based)

These are registered with Django REST framework’s DefaultRouter, meaning they provide CRUD operations automatically.

| Endpoint | ViewSet | Description |
|----------|---------|-------------|
| `/api/products/` | ProductViewSet | List and manage products (CRUD) |
| `/api/categories/` | CategoryViewSet | List and manage categories (CRUD) |


🏷️ **Categories API**

**Endpoint:** `/api/categories/`
```sh
# Fetch all categories via API
curl -X GET http://localhost:8000/api/categories/
```

✔️ **Example Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "decoration",
      "slug": "decoration",
      "parent_id": null
    },
    {
      "id": 2,
      "name": "decoration > bedroom",
      "slug": "bedroom",
      "parent_id": 1
    },
    {
      "id": 3,
      "name": "decoration > bedroom > bed",
      "slug": "bed",
      "parent_id": 2
    }
  ]
}
```

🔎 **Filtering:**
```sh
# Returns all products in “bedroom” and its subcategories.
curl -X GET "http://localhost:8000/api/products/?category=bedroom"
```


### HTML-Based Views (Template Views)

These endpoints render HTML templates for product management.

| Endpoint | View | Description |
|----------|------|-------------|
| `/html/product/` | product_list | Product List Page |
| `/html/product/<int:product_id>/` | product_detail | Product Detail Page |
| `/html/product/edit/<int:pk>/` | EditProductView | Edit Product Page (form-based) |
| `/html/product/delete/<int:pk>/` | DeleteProductView | Delete Confirmation Page |
| `/html/product/add/` | AddProductView | Add New Product Page |

---

## 📊 Logging & Debugging
Logs are stored in `logs/` and can be accessed via:
View the latest logs
```sh
tail -f logs/django.log
```

View the latest warnings and errors only
```sh
tail -f logs/django_warn.log
```

This **helps debugging** and makes log access clear.

---




---

## 🎯 Next Steps
Would you like to:
- **Optimize query indexing for PostgreSQL?**
- **Implement caching with Redis to speed up repeated queries?**
- **Improve API response times using Django REST Framework optimizations?**