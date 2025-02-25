# Django Web Crawler with Docker and Secrets

This project is a Django-based web crawler that uses PostgreSQL, containerized with Docker and secured using Docker Secrets.

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

Optionally, Save the Image for Deployment

If deploying to another server, save and load the image manually:

```sh
docker save -o django-crawler.tar django-crawler
# Copy it to another server, then load it:
docker load -i django-crawler.tar
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
CONTAINER ID   IMAGE        STATUS         PORTS
123abc456def   django_app   Up 2 minutes   0.0.0.0:8000->8000/tcp
789xyz123ghi   postgres:16  Up 2 minutes   0.0.0.0:5432->5432/tcp
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

## 🚀 Performance Optimizations
- Bulk insert and update operations have been implemented to significantly improve database performance.
- Crawler now processes products efficiently using `bulk_create` and `bulk_update` to reduce query load.

---

## 📜 Logging & Debugging
Logs are stored in `logs/` and can be accessed via:
```sh
# View the latest logs
tail -f logs/django.log

# View the latest warnings and errors only
tail -f logs/django_warn.log
```

This **helps debugging** and makes log access clear.

---

## **Document the Improved Category Handling**
Since you've improved **category parent-child relationships**, document how categories work.

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



---

## 🎯 Next Steps
Would you like to:
- **Optimize query indexing for PostgreSQL?**
- **Implement caching with Redis to speed up repeated queries?**
- **Improve API response times using Django REST Framework optimizations?**