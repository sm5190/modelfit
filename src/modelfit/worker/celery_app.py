from celery import Celery

from modelfit.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "modelfit",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["modelfit.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    timezone="UTC",
)
