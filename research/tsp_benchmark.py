import time
from research.advanced_solvers import load_tsplib_instances

def run_tsp_benchmark():
    print("--- TSPLIB Benchmark (Basin Escape v3.2) ---")
    tsps = load_tsplib_instances("datasets/tsplib/tsp_instances_dataset.csv")

    results = []
    for t in tsps[:5]: # Benchmark first 5
        t0 = time.perf_counter()
        best_tour, best_dist = t.solve(max_iter=100000, verbose=False)
        elapsed = time.perf_counter() - t0
        results.append((t.name, best_dist, elapsed))
        print(f"  {t.name:<10} | Best Dist: {best_dist:>10.2f} | Time: {elapsed:>6.2f}s")

if __name__ == "__main__":
    run_tsp_benchmark()
