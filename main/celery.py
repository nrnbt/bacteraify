from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'run-my-task-every-minute': {
        'task': 'main.tasks.train_model_taskZ',
        # 'schedule': crontab(minute='*/1'),
        'schedule': crontab(hour=1, minute=0),  # every night at 1:00 AM
    },
}
