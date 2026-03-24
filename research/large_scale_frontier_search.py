import sys
import os
import time
import json
import random

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import run_hybrid_sa, run_fiber_structured_sa

def orchestrate():
    configs = [
        {"name": "P1", "m": 4, "k": 4, "engine": "fiber", "iters": 15_000_000},
        {"name": "P2", "m": 6, "k": 3, "engine": "hybrid", "iters": 15_000_000},
        {"name": "P3", "m": 8, "k": 3, "engine": "hybrid", "iters": 15_000_000},
    ]

    print("=== Large-Scale Frontier Search Orchestrator ===")

    for cfg in configs:
        name = cfg["name"]
        m, k = cfg["m"], cfg["k"]
        iters = cfg["iters"]
        engine_type = cfg["engine"]

        print(f"\nStarting {name} (m={m}, k={k}) with {iters:,} iterations using {engine_type} engine...")
        t0 = time.perf_counter()

        # Use a random seed for variability
        seed = random.randint(0, 1000000)

        if engine_type == "fiber":
            sol, stats = run_fiber_structured_sa(m=m, k=k, max_iter=iters, seed=seed, verbose=True)
        else:
            sol, stats = run_hybrid_sa(m=m, k=k, max_iter=iters, seed=seed, verbose=True)

        dt = time.perf_counter() - t0
        print(f"{name} Finished in {dt:.2f}s")
        print(f"Best score reached: {stats['best']}")

        if sol:
            print(f"SUCCESS: {name} solved!")
            with open(f"solution_{name}.json", "w") as f:
                json.dump(sol, f)
        else:
            print(f"FAILED: {name} did not reach score 0.")

if __name__ == "__main__":
    orchestrate()
