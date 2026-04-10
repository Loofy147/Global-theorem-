import numpy as np
import time
import os
import shutil
from STRATOS_CORE_V2 import TopologicalCleanUpGate, StratosEngineV2

def benchmark_cleanup():
    print("\n--- Benchmarking TopologicalCleanUpGate ---")
    dim = 4096
    gate = TopologicalCleanUpGate(dim=dim)
    n_items = 1500

    # Registration
    vectors = [np.random.normal(0, 1/np.sqrt(dim), dim) for _ in range(n_items)]
    for i, v in enumerate(vectors):
        gate.register(f"item_{i}", v)

    noisy_v = vectors[n_items // 2] + np.random.normal(0, 0.1, dim)

    start = time.perf_counter()
    for _ in range(100):
        gate.cleanup(noisy_v)
    end = time.perf_counter()
    print(f"Cleanup (100 calls, {n_items} items): {end - start:.4f}s")

def benchmark_hrr():
    print("\n--- Benchmarking HRR Operations ---")
    dim = 4096
    engine = StratosEngineV2(dim=dim)
    a = np.random.normal(0, 1/np.sqrt(dim), dim)
    b = np.random.normal(0, 1/np.sqrt(dim), dim)

    start = time.perf_counter()
    for _ in range(1000):
        engine.bind(a, b)
    end = time.perf_counter()
    print(f"Bind (1000 calls): {end - start:.4f}s")

    composite = engine.bind(a, b)
    start = time.perf_counter()
    for _ in range(1000):
        engine.unbind(composite, a)
    end = time.perf_counter()
    print(f"Unbind (1000 calls): {end - start:.4f}s")

def benchmark_engine_query():
    print("\n--- Benchmarking StratosEngineV2.query ---")
    dim = 4096
    test_dir = "./BENCHMARK_MEMORY"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    engine = StratosEngineV2(dim=dim, memory_dir=test_dir)

    # Ingest some data
    n_ingest = 100
    for i in range(n_ingest):
        engine.ingest_semantic(f"test.item_{i}", lambda x: x)

    start = time.perf_counter()
    for i in range(n_ingest):
        engine.query(f"test.item_{i}")
    end = time.perf_counter()
    print(f"Query ({n_ingest} calls): {end - start:.4f}s")

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    benchmark_cleanup()
    benchmark_hrr()
    benchmark_engine_query()
