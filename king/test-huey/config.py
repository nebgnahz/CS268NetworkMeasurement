# config.py
from huey import BaseConfiguration, Invoker
from huey.backends.redis_backend import RedisBlockingQueue


queue = RedisBlockingQueue('test-queue', host='localhost', port=6379)
invoker = Invoker(queue)


class Configuration(BaseConfiguration):
    QUEUE = queue
    THREADS = 4
