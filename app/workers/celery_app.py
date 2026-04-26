from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery = Celery(
    "audiocrag",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

celery.conf.task_track_started = True