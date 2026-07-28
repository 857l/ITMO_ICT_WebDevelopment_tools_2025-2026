import threading
import time


def calculate_sum(start, end, result, index):
    total = 0
    for i in range(start, end + 1):
        total += i
    result[index] = total


def run_threading(n, num_threads=4):
    threads = []
    results = [0] * num_threads
    step = n // num_threads

    start_time = time.time()

    for i in range(num_threads):
        start = i * step + 1
        end = (i + 1) * step if i != num_threads - 1 else n
        thread = threading.Thread(target=calculate_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    end_time = time.time()

    return total_sum, end_time - start_time


if __name__ == "__main__":
    N = 100_000_000
    total, duration = run_threading(N)
    print(f"Потоки: Сумма = {total}, Время = {duration:.4f}сек")
