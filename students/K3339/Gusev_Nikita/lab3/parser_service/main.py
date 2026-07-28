import aiohttp
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from models import ScrapedPage, get_session, init_db

app = FastAPI(title="Parser Service")


class ParseRequest(BaseModel):
    url: str


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def health():
    return {"status": "ok", "service": "parser"}


async def parse_and_save(url: str) -> str:
    """
    Логика взята из lab2/task2/scrape_async.py:
    скачивает страницу, достаёт <title> и сохраняет запись в БД.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"

    with get_session() as db_session:
        page = ScrapedPage(url=url, title=title, approach="async")
        db_session.add(page)
        db_session.commit()

    return title


@app.post("/parse")
async def parse(request: ParseRequest):
    """
    Эндпоинт, который вызывается основным FastAPI-приложением (или Celery-воркером).
    Скачивает страницу по url, сохраняет заголовок в БД, возвращает результат.
    """
    try:
        title = await parse_and_save(request.url)
        return {"message": "Parsing completed", "url": request.url, "title": title}
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch url: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
