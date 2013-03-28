from celery import Celery

redis_db = 'redis://localhost:6379/0'

celery = Celery('tasks', broker=redis_db, backend=redis_db)


@celery.task
def add(x, y):
    return x + y
