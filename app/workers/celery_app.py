from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "frappe_stream",
    broker=settings.redis_url,
    backend=settings.redis_url.replace("/0", "/1")
)

celery_app.conf.task_routes = {
    "app.workers.video_tasks.process_video":    {"queue": "long"},
    "app.workers.video_tasks.gen_thumbnail":    {"queue": "short"},
}

celery_app.conf.beat_schedule = {
    "recover-stuck-jobs": {
        "task": "app.workers.video_tasks.recover_stuck_jobs",
        "schedule": 300.0,
    },
}
