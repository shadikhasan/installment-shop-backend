from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Schedule tasks using Celery Beat
app.conf.beat_schedule = {
    'send_due_reminders_task': {
        'task': 'myapp.tasks.send_due_reminders',  # Adjust task path
        'schedule': crontab(minute=0, hour=0),  # Example: run daily at midnight
        'args': (3,)  # Pass the number of days before due to remind (e.g., 3 days)
    },
}
