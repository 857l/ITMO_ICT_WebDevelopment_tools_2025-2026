import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import PARSER_SERVICE_URL
from celery_app import celery_app
from tasks import parse_url_task

router = APIRouter(prefix="/parser", tags=["Parser"])


class ParseRequest(BaseModel):
    url: str


@router.post("/parse")
def parse_sync(request: ParseRequest):
    """
    Подзадача 2: клиент отправляет URL сюда, FastAPI сам обращается
    к parser_service (запущенному в отдельном контейнере) и сразу
    возвращает клиенту результат.
    """
    try:
        response = requests.post(
            f"{PARSER_SERVICE_URL}/parse", json={"url": request.url}, timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Parser service error: {e}")


@router.post("/parse-async")
def parse_async(request: ParseRequest):
    """
    Подзадача 3: URL кладётся в очередь Celery (брокер — Redis),
    задачу выполнит воркер в фоне. Клиент сразу получает task_id
    и может позже проверить статус через /parser/status/{task_id}.
    """
    task = parse_url_task.delay(request.url)
    return {"status": "queued", "task_id": task.id}


@router.get("/status/{task_id}")
def parse_status(task_id: str):
    """Проверка статуса и результата фоновой задачи парсинга."""
    result = celery_app.AsyncResult(task_id)
    response = {"task_id": task_id, "status": result.status}
    if result.ready():
        try:
            response["result"] = result.get(timeout=1)
        except Exception as e:
            response["error"] = str(e)
    return response
