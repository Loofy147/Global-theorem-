import time
import os
from research.fso_refinery import FSORefinery

def bench_refinery():
    print("\n--- Benchmarking Repository Smelting (Parallel vs Sequential) ---")
    m = 101
    refinery = FSORefinery(m)

    # Target research directory
    target_dir = "./research"

    start = time.perf_counter()
    units = refinery.refinery_process(target_dir)
    end = time.perf_counter()
    print(f"Parallel Smelting ({len(units)} units): {end - start:.4f}s")

    # Note: We don't have a direct serial method anymore in the class,
    # but we can simulate it by setting cpu_count=1 if we modified the class to accept it.
    # For now, we compare against the fact that it used to be serial.

if __name__ == "__main__":
    bench_refinery()
