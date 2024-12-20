from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_email.settings')

app = Celery('auto_email')

# Use a string here to avoid importing the Django settings file directly.
app.config_from_object('django.conf:settings', namespace='CELERY')


# Discover tasks in installed apps automatically.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Task to run at every minute:
    'cheack emails to sent every minute ': {
        'task': 'scheduler.tasks.trigger_scheduled_emails',
        'schedule': crontab(),
    },
    'remove_unverified_users': {
        'task': 'accounts.tasks.remove_unverified_users',
        'schedule': crontab(hour=0, minute=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
