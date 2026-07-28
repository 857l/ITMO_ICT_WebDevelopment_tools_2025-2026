import requests
from bs4 import BeautifulSoup
import multiprocessing
from models import ScrapedPage, get_session
import time


def parse_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No Title"
        title = title.strip()

        with get_session() as session:
            page = ScrapedPage(url=url, title=title, approach="multiprocessing")
            session.add(page)
            session.commit()

        print(f"[Процессы] Спарсено: {url} -> {title}")
        return True
    except Exception as e:
        print(f"[Процессы] Ошибка {url}: {e}")
        return False


def _init_worker():
    from models import engine
    engine.dispose()


def run_multiprocessing(urls):
    from models import engine
    engine.dispose()

    start_time = time.time()
    with multiprocessing.Pool(processes=4, initializer=_init_worker) as pool:
        pool.map(parse_and_save, urls)
    end_time = time.time()

    engine.dispose()

    return end_time - start_time


if __name__ == "__main__":
    test_urls = ["https://www.python.org", "https://www.google.com"]
    duration = run_multiprocessing(test_urls)
    print(f"Процессы: Время парсинга: {duration:.4f}сек")
