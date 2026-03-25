import multiprocessing as mp
import time
import json
import os
import sys

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import run_fiber_structured_sa

def worker(seed):
    m, k = 4, 4
    iters = 10_000_000
    print(f"Worker {seed} started.")
    sol, stats = run_fiber_structured_sa(m=m, k=k, seed=seed, max_iter=iters, verbose=False)
    if sol:
        print(f"Worker {seed} FOUND SOLUTION!")
        # Save solution
        filename = f"research/p1_sol_{seed}.json"
        with open(filename, "w") as f:
            # Convert tuple keys to strings
            json.dump({str(k_): v_ for k_, v_ in sol.items()}, f)
        return True
    return False

def main():
    # Use different seeds to explore more space
    seeds = [12, 13, 15, 17, 19, 23, 29, 31]
    with mp.Pool(processes=min(len(seeds), mp.cpu_count())) as pool:
        pool.map(worker, seeds)

if __name__ == "__main__":
    main()
