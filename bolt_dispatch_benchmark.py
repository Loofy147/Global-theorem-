import time
import os
import sys
from fso_stratified_ingestor import DirectConsumer, FSOTopology

def bench_dispatch():
    print("\n--- Benchmarking Logic Dispatch (Cached vs Uncached) ---")
    topo = FSOTopology(m=31)
    consumer = DirectConsumer(topo)

    # 1. Warm up provisioned packages
    consumer.auto_provision("math")

    # 2. Benchmark First Call (Uncached)
    start = time.perf_counter()
    res = consumer.execute("math.sin", x=0.5)
    end = time.perf_counter()
    print(f"First Dispatch (math.sin): {end - start:.6f}s")

    # 3. Benchmark Repeated Calls (Cached)
    start = time.perf_counter()
    for _ in range(1000):
        res = consumer.execute("math.sin", x=0.5)
    end = time.perf_counter()
    print(f"1000 Cached Dispatches: {end - start:.6f}s (Average: {(end - start)/1000:.8f}s)")

if __name__ == "__main__":
    bench_dispatch()
