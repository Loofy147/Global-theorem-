import numpy as np
import time
import os
import shutil
from STRATOS_CORE_V2 import StratosEngineV2

def benchmark_repeated_queries():
    print("\n--- Benchmarking Repeated Queries (Same Bucket) ---")
    dim = 4096
    test_dir = "./QUERY_BENCHMARK_MEMORY"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    engine = StratosEngineV2(dim=dim, memory_dir=test_dir)

    # Ingest 50 items into the 'math' bucket
    items = {f"math.item_{i}": lambda x: x for i in range(50)}
    for name, obj in items.items():
        engine.ingest_semantic(name, obj)

    # Baseline: 500 queries to 'math' bucket items
    start = time.perf_counter()
    for _ in range(10): # 10 passes of 50 items
        for i in range(50):
            engine.query(f"math.item_{i}")
    end = time.perf_counter()
    print(f"Total time (500 total, 50 unique items, 1 bucket): {end - start:.4f}s")

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    benchmark_repeated_queries()
