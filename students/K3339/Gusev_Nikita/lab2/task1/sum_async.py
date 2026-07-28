import asyncio
import time


async def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
        if i % 1_000_000 == 0:
            await asyncio.sleep(0)
    return total


async def run_async(n, num_tasks=4):
    step = n // num_tasks
    tasks = []

    start_time = time.time()

    for i in range(num_tasks):
        start = i * step + 1
        end = (i + 1) * step if i != num_tasks - 1 else n
        tasks.append(calculate_sum(start, end))

    results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.time()

    return total_sum, end_time - start_time


if __name__ == "__main__":
    N = 100_000_000
    total, duration = asyncio.run(run_async(N))
    print(f"Асинхронность: Сумма = {total}, Время = {duration:.4f}сек")
