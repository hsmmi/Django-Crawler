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

## 🎯 Next Steps
Would you like to:
- **Automate deployment with GitHub Actions?**
- **Configure logging and monitoring?**
- **Enhance the crawler with scheduling using Celery?**

Let us know what’s next! 🚀
