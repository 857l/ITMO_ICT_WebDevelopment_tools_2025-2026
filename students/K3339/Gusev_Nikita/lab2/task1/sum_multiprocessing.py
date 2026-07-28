import multiprocessing
import time


def calculate_sum(range_tuple):
    start, end = range_tuple
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


def run_multiprocessing(n, num_processes=4):
    step = n // num_processes
    ranges = []

    for i in range(num_processes):
        start = i * step + 1
        end = (i + 1) * step if i != num_processes - 1 else n
        ranges.append((start, end))

    start_time = time.time()

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(calculate_sum, ranges)

    total_sum = sum(results)
    end_time = time.time()

    return total_sum, end_time - start_time


if __name__ == "__main__":
    N = 100_000_000
    total, duration = run_multiprocessing(N)
    print(f"Процессы: Сумма = {total}, Время = {duration:.4f}сек")
