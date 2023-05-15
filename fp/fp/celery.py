import os
from celery import Celery
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE','fp.settings')

app = Celery('fp')

app.config_from_object('django.conf:settings',namespace='CELERY')


app.conf.beat_schedule = {
    'account_update_1s': {
        'task': 'real_time.tasks.trading_account_update',
        'schedule': timedelta(seconds=3)
    }
}

app.autodiscover_tasks()