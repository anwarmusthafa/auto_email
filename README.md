# Auto Email Scheduler with Django Rest Framework and Celery

A Django Rest Framework-based project that allows users to schedule emails for future delivery. The project uses Celery for task scheduling and Redis as a message broker.
## Features

- User registration with OTP verification
- JWT-based authentication for secure access
- Schedule emails with a specified date and time
- Automatic email delivery using Celery and periodic tasks

## Prerequisites
To run this project on your local machine, ensure you have the following installed:

- Python (>= 3.8)
- Django (>= 4.0)
- PostgreSQL or any database(here used sqllite)
- Redis
- Celery
## Installation Steps

1. Clone the Repository

```bash
git clone https://github.com/your-username/auto_email_scheduler.git
cd auto_email_scheduler
```
2. Set Up a Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```
3. Install Dependencies

```bash
pip install -r requirements.txt
```
4. Configure environment variables: Create a .env file in the project root and add:
```bash
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_password
CELERY_BROKER_URL=redis://localhost:6383/0
```

5. Configure Redis for Celery

```bash
install redis on your machine
start redis server on port 6383
update your redis path in settings.py file
```
6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
7. Create a Superuser
```bash
 python manage.py createsuperuser
```
8. Start the Celery Worker
```bash
 celery -A auto_email worker --loglevel=info
```
9. Start the Celery Beat Scheduler
```bash
 celery -A auto_email beat --loglevel=info
```

## Task Scheduling with Celery
- Celery is used to send and schedule emails.
- A periodic task (trigger_scheduled_emails) runs every minute to check and send emails.
- Celery results will be available in django-db , can visible in django admin.
- Periodic tasks can manage from django admin interface.

## Note
- Replace placeholders in .env file with your actual credentials.
- Ensure Redis is running locally (redis-server).
- Ensure Celery Worker and Celery Beat are running.
- Test all endpoints using tools like Postman or cURL.
- Use the access token received from login for all protected API requests in the Authorization header.



## Documentation
https://documenter.getpostman.com/view/16149452/2sAYBd6nLD
