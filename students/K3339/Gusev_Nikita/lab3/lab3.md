# Лабораторная работа 3. Docker и очереди задач

**Студент:** Гусев Никита
**Группа:** K3339
**Тема:** Упаковка FastAPI-приложения в Docker, взаимодействие сервисов и работа с очередью фоновых задач.

## Цель работы

Контейнеризировать приложение из лабы 1 (Personal Finance Service) вместе с базой данных и парсером из лабы 2 с помощью Docker и Docker Compose. Настроить два способа вызова парсинга: прямой HTTP-запрос к отдельному сервису и постановку задачи в очередь через Celery/Redis. Сравнить оба подхода.

## Архитектура проекта

Все сервисы развёрнуты в единой сети Docker Compose:

1. **db** — PostgreSQL, общая база данных для финансового приложения и для результатов парсинга.
2. **redis** — брокер сообщений и backend результатов для Celery.
3. **app** — основное FastAPI-приложение (Personal Finance Service из лабы 1) + новый роутер `/parser/*`.
4. **parser** — отдельный микросервис на FastAPI, оборачивающий асинхронный парсер (`scrape_async.py`) из лабы 2, эндпоинт `POST /parse`.
5. **celery_worker** — тот же образ, что и `app`, но с командой `celery worker` — разбирает фоновые задачи парсинга.

Для корректного порядка запуска у `db` настроен `healthcheck` (`pg_isready`), от него зависят `app`, `parser` и `celery_worker` — они стартуют только после готовности базы.

```yaml
db:
  image: postgres:16
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
    interval: 5s
    timeout: 5s
    retries: 5
```

## Dockerfile

Использованы два похожих `Dockerfile` (для `app`/`celery_worker` и для `parser`), оба на базе `python:3.11-slim`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`celery_worker` использует тот же образ `app`, но переопределяет команду прямо в `docker-compose.yml`:

```yaml
celery_worker:
  build: ./app
  command: celery -A celery_app worker --loglevel=info
```

## Два подхода к парсингу

### 1. Синхронный вызов парсера по HTTP

Отдельный контейнер `parser` слушает порт 8001 внутри докер-сети. Основное приложение обращается к нему из роутера `/parser/parse`:

```python
@router.post("/parse")
def parse_sync(request: ParseRequest):
    response = requests.post(
        f"{PARSER_SERVICE_URL}/parse", json={"url": request.url}, timeout=15
    )
    response.raise_for_status()
    return response.json()
```

Клиент делает запрос и ждёт, пока `parser` скачает страницу, распарсит `<title>` и сохранит запись в БД — и только после этого получает ответ.

### 2. Очередь задач на Celery + Redis

Эндпоинт `/parser/parse-async` кладёт URL в очередь и сразу возвращает `task_id`, не дожидаясь результата:

```python
@router.post("/parse-async")
def parse_async(request: ParseRequest):
    task = parse_url_task.delay(request.url)
    return {"status": "queued", "task_id": task.id}
```

Саму работу выполняет фоновый воркер, задача обращается к тому же `parser`-сервису по HTTP:

```python
@celery_app.task(name="tasks.parse_url_task", bind=True, max_retries=3)
def parse_url_task(self, url: str):
    response = requests.post(f"{PARSER_SERVICE_URL}/parse", json={"url": url}, timeout=15)
    response.raise_for_status()
    return response.json()
```

Статус и результат задачи проверяются отдельным эндпоинтом:

```python
@router.get("/status/{task_id}")
def parse_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    response = {"task_id": task_id, "status": result.status}
    if result.ready():
        response["result"] = result.get(timeout=1)
    return response
```

## Тестирование

Проект поднимается одной командой:

```powershell
docker compose up --build
```

Все 5 контейнеров стартовали без ошибок: `db` — healthy, `redis` — готов принимать соединения, `parser` и `app` подняли Uvicorn на портах 8001 и 8000, `celery_worker` подключился к Redis и зарегистрировал задачу `tasks.parse_url_task`.

**Синхронный вызов:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/parser/parse" -Method POST `
  -ContentType "application/json" -Body '{"url": "https://www.python.org"}'
```
```
message           url                    title
-------           ---                    -----
Parsing completed https://www.python.org Welcome to Python.org
```

**Асинхронный вызов через очередь:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/parser/parse-async" -Method POST `
  -ContentType "application/json" -Body '{"url": "https://www.python.org"}'
```
```
status task_id
------ -------
queued 900a956e-114c-4fd9-ab9c-83c8ece22afc
```

**Проверка статуса задачи:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/parser/status/900a956e-114c-4fd9-ab9c-83c8ece22afc" -Method GET
```
```
task_id                              status  result
-------                              ------  ------
900a956e-114c-4fd9-ab9c-83c8ece22afc SUCCESS @{message=Parsing completed; url=https://www.python.org; title=Welcome to Python.org}
```

**Проверка данных в БД** (через `docker exec -it lab3-db-1 psql -U postgres -d lab_db`):

```sql
lab_db=# SELECT * FROM scrapedpage;
 id |          url           |         title         | approach
----+------------------------+-----------------------+----------
  1 | https://www.python.org | Welcome to Python.org | async
  2 | https://www.python.org | Welcome to Python.org | async
(2 rows)
```

Обе записи — от синхронного и от асинхронного вызова — сохранились в общей базе `lab_db`, которая используется и финансовым приложением из лабы 1.

## Сравнение подходов

| Критерий | Вызов по HTTP (`/parser/parse`) | Очередь Celery (`/parser/parse-async`) |
| :--- | :--- | :--- |
| **Время ответа клиенту** | Долгое — ждёт завершения парсинга | Мгновенное — задача уходит в фон |
| **Сложность инфраструктуры** | Проще — только два FastAPI-сервиса | Сложнее — нужен Redis и отдельный worker |
| **Устойчивость к сбоям** | Ниже — ошибка сети сразу возвращается клиенту | Выше — задачу можно ретраить (`max_retries=3`) |
| **Идеальный сценарий** | Один быстрый запрос, где важен мгновенный результат | Массовый парсинг, длительные операции, где клиент не должен ждать |

## Вывод

Контейнеризация с Docker Compose позволила одной командой поднять пять связанных сервисов — приложение, БД, парсер, брокер и воркер — без ручной настройки окружения на хосте. Сравнение двух способов вызова парсера показало ожидаемое: прямой HTTP-вызов проще в реализации, но блокирует клиента на время работы парсера, тогда как очередь на Celery/Redis усложняет архитектуру, зато делает API отзывчивым и добавляет встроенные ретраи при сбоях — то есть больше подходит для длительных или ненадёжных операций вроде парсинга внешних сайтов.