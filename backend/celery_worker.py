from celery import Celery

app = Celery(
    'celery_worker',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    #broker='redis://127.0.0.1:6379/0',
    #backend='redis://127.0.0.1:6379/0',
    broker_connection_retry_on_startup=True,
    include=['app.tasks']
)

