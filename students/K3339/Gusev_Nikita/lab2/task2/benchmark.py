import asyncio

from scrape_threading import run_threading
from scrape_multiprocessing import run_multiprocessing
from scrape_async import run_async
from models import init_db


def main():
    urls = [
        "https://www.python.org",
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://www.google.com",
        "https://www.reddit.com",
        "https://www.medium.com",
        "https://www.digitalocean.com",
    ]

    print("Инициализация базы данных...")
    init_db()

    print(f"Запуск бенчмарка задачи 2 (Парсинг {len(urls)} URL)...")

    print("Запуск через потоки...")
    time_t = run_threading(urls)
    print(f"Время: {time_t:.4f}сек")

    print("Запуск через процессы...")
    time_m = run_multiprocessing(urls)
    print(f"Время: {time_m:.4f}сек")

    print("Запуск через асинхронность...")
    time_a = asyncio.run(run_async(urls))
    print(f"Время: {time_a:.4f}сек")

    print("-" * 40)
    print(f"{'Метод':<20} | {'Время (сек)':<10}")
    print("-" * 40)
    print(f"{'Потоки':<20} | {time_t:<10.4f}")
    print(f"{'Процессы':<20} | {time_m:<10.4f}")
    print(f"{'Асинхронность':<20} | {time_a:<10.4f}")
    print("-" * 40)


if __name__ == "__main__":
    main()
