import time
import os
import shutil
import numpy as np
from STRATOS_CORE_V2 import StratosEngineV2

def bench_ingest():
    dim = 4096
    memory_dir = "./INGEST_BENCHMARK"
    if os.path.exists(memory_dir):
        shutil.rmtree(memory_dir)

    engine = StratosEngineV2(dim=dim, memory_dir=memory_dir)

    # 20 items to reduce overhead of sig extraction in benchmark
    items = {f"bench.item_{i}": lambda x: x for i in range(20)}

    print("--- Benchmarking Serial Ingestion ---")
    start = time.perf_counter()
    for name, obj in items.items():
        engine.ingest_semantic(name, obj)
    end = time.perf_counter()
    print(f"Serial Ingestion (20 items): {end - start:.4f}s")

    if os.path.exists(memory_dir):
        shutil.rmtree(memory_dir)

    engine = StratosEngineV2(dim=dim, memory_dir=memory_dir)
    print("\n--- Benchmarking Batch Ingestion ---")
    start = time.perf_counter()
    engine.batch_ingest_semantic(items)
    end = time.perf_counter()
    print(f"Batch Ingestion (20 items): {end - start:.4f}s")

    if os.path.exists(memory_dir):
        shutil.rmtree(memory_dir)

if __name__ == "__main__":
    bench_ingest()
