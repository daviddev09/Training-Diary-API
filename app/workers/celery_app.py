from celery import Celery

from app.core.config import settings

redis_broker_url = f"redis://{settings.redis_host}:{settings.redis_port}/3"
app = Celery(
    "tasks",
    broker=redis_broker_url,
    imports=["app.workers.smtp_worker", "app.workers.pdf_worker"],
)
