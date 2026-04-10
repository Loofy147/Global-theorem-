import time
import os
import shutil
import numpy as np
from research.fso_ptfs import Persistent_Torus_Core

def bench_ptfs():
    storage_dir = "./BENCHMARK_PTFS"
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)

    ptfs = Persistent_Torus_Core(m=1000003, dim=1024, storage_dir=storage_dir)

    n_facts = 50 # Reduced count for faster clear signal
    facts = [(f"subject_{i}", f"payload_{i}") for i in range(n_facts)]

    print("--- Benchmarking PTFS Serial Ingestion ---")
    start = time.perf_counter()
    for s, p in facts:
        ptfs.ingest_fact(s, p)
    end = time.perf_counter()
    print(f"Serial Ingestion ({n_facts} facts): {end - start:.4f}s")

    # Flush cache to disk before next test
    ptfs.flush_all()

    # Create new instance to test batch with clean state
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)
    ptfs_batch = Persistent_Torus_Core(m=1000003, dim=1024, storage_dir=storage_dir)

    print("\n--- Benchmarking PTFS Batch Ingestion ---")
    start = time.perf_counter()
    ptfs_batch.ingest_facts_batch(facts)
    # Ensure it hits disk for fair comparison
    ptfs_batch.flush_all()
    end = time.perf_counter()
    print(f"Batch Ingestion ({n_facts} facts): {end - start:.4f}s")

    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)

if __name__ == "__main__":
    bench_ptfs()
