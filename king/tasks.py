from celery import Celery

redis_db = 'redis://localhost:6379/0'

celery = Celery('tasks', broker=redis_db, backend=redis_db)
celery.conf.update(
    BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 300}, #5 minutes
)

@celery.task
def add(x, y):
    return x + y
