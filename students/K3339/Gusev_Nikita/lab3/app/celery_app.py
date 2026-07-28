from celery import Celery

from core.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "lab3_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Пример периодической задачи (бонус, необязательно):
# celery_app.conf.beat_schedule = {
#     "ping-every-hour": {
#         "task": "tasks.ping_parser",
#         "schedule": 3600.0,
#     },
# }
