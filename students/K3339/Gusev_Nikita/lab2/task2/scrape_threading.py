import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from models import ScrapedPage, get_session
import time


def parse_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No Title"
        title = title.strip()

        with get_session() as session:
            page = ScrapedPage(url=url, title=title, approach="threading")
            session.add(page)
            session.commit()

        print(f"[Потоки] Спарсено: {url} -> {title}")
        return True
    except Exception as e:
        print(f"[Потоки] Ошибка {url}: {e}")
        return False


def run_threading(urls):
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        list(executor.map(parse_and_save, urls))
    end_time = time.time()
    return end_time - start_time


if __name__ == "__main__":
    test_urls = ["https://www.python.org", "https://www.google.com"]
    duration = run_threading(test_urls)
    print(f"Потоки: Время парсинга: {duration:.4f}сек")
