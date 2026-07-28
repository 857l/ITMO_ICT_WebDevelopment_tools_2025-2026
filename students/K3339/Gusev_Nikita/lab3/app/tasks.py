import requests

from celery_app import celery_app
from core.config import PARSER_SERVICE_URL


@celery_app.task(name="tasks.parse_url_task", bind=True, max_retries=3)
def parse_url_task(self, url: str):
    """
    Фоновая задача: обращается к parser_service (отдельный контейнер),
    который скачивает страницу и сохраняет заголовок в БД.
    """
    try:
        response = requests.post(
            f"{PARSER_SERVICE_URL}/parse", json={"url": url}, timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        # ретраим с задержкой на случай, если parser временно недоступен
        raise self.retry(exc=exc, countdown=5)


# Пример периодической задачи (бонус):
# @celery_app.task(name="tasks.ping_parser")
# def ping_parser():
#     requests.get(f"{PARSER_SERVICE_URL}/")
