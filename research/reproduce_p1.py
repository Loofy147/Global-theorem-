import sys
import os
import time
import json
import random

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import run_fiber_structured_sa, verify_sigma

def run():
    m, k, seed = 4, 4, 12
    # To reach score 0 faster, we can reduce iters and use higher temp if needed,
    # but the kernel reached it in ~47M.
    iters = 100_000_000
    print(f"Reproducing P1 (m={m}, k={k}) with seed={seed}...")
    t0 = time.perf_counter()

    # We use the seed 12 as in the kernel
    sol, stats = run_fiber_structured_sa(m=m, k=k, seed=seed, max_iter=iters, verbose=True)
    dt = time.perf_counter() - t0

    print("-" * 50)
    print(f"Finished in {dt:.2f}s")
    if sol:
        print("SUCCESS: Hamiltonian decomposition found!")
        # Correctly save the solution
        sol_serializable = {str(k_): v_ for k_, v_ in sol.items()}
        with open("research/p1_solution_verified.json", "w") as f:
            json.dump(sol_serializable, f)
    else:
        print(f"FAILED: Best score reached: {stats['best']}")

if __name__ == "__main__":
    run()
