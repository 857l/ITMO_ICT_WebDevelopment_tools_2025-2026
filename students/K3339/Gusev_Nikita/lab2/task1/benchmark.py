import asyncio

from sum_threading import run_threading
from sum_multiprocessing import run_multiprocessing
from sum_async import run_async


def main():
    N = 100_000_000
    print(f"Запуск бенчмарка задачи 1 (Сумма до {N:,})...")

    print("Запуск через потоки...")
    sum_t, time_t = run_threading(N)
    print(f"Результат: {sum_t}, Время: {time_t:.4f}сек")

    print("Запуск через процессы...")
    sum_m, time_m = run_multiprocessing(N)
    print(f"Результат: {sum_m}, Время: {time_m:.4f}сек")

    print("Запуск через асинхронность...")
    sum_a, time_a = asyncio.run(run_async(N))
    print(f"Результат: {sum_a}, Время: {time_a:.4f}сек")

    print("-" * 40)
    print(f"{'Метод':<20} | {'Время (сек)':<10}")
    print("-" * 40)
    print(f"{'Потоки':<20} | {time_t:<10.4f}")
    print(f"{'Процессы':<20} | {time_m:<10.4f}")
    print(f"{'Асинхронность':<20} | {time_a:<10.4f}")
    print("-" * 40)


if __name__ == "__main__":
    main()
