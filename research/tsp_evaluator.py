import math, random, time, json, os
from typing import List, Tuple, Dict, Any, Optional

def is_valid_tour(tour: List[int], n: int) -> bool:
    if len(tour) != n: return False
    return len(set(tour)) == n

def calculate_tour_length(tour: List[int], dist_matrix: List[List[float]]) -> float:
    n = len(tour)
    length = 0.0
    for i in range(n):
        length += dist_matrix[tour[i]][tour[(i+1)%n]]
    return length

class TSPInstance:
    def __init__(self, name: str, coords: List[Tuple[float, float]]):
        self.name = name
        self.coords = coords
        self.n = len(coords)
        self.dist_matrix = [[0.0]*self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                self.dist_matrix[i][j] = math.sqrt((coords[i][0]-coords[j][0])**2 + (coords[i][1]-coords[j][1])**2)

def load_data(csv_path: str) -> List[TSPInstance]:
    import pandas as pd
    df = pd.read_csv(csv_path)
    instances = []
    for _, row in df.iterrows():
        name = str(row['TSP_Instance'])
        coords = []
        for i in range(1, 151):
            x, y = row.get(f'City_{i}_X'), row.get(f'City_{i}_Y')
            if pd.isna(x) or pd.isna(y): break
            coords.append((float(x), float(y)))
        if coords: instances.append(TSPInstance(name, coords))
    return instances

def run_evaluation(instance: TSPInstance, solver_fn: Any, n_runs=10, max_iter=50000):
    print(f"\n--- Evaluating {instance.name} ({instance.n} cities) ---")

    # 1. Baseline: Random
    r_lengths = []
    for s in range(5):
        tour = list(range(instance.n)); random.Random(s).shuffle(tour)
        r_lengths.append(calculate_tour_length(tour, instance.dist_matrix))
    r_best = min(r_lengths)

    # 2. Baseline: NN
    from research.advanced_solvers import TSPSolver
    nn_tour = TSPSolver(instance.name, instance.coords).nearest_neighbor()
    nn_len = calculate_tour_length(nn_tour, instance.dist_matrix)

    lengths = []
    times = []

    for i in range(n_runs):
        t0 = time.perf_counter()
        tour, length = solver_fn(instance, max_iter=max_iter, seed=i*100)
        elapsed = time.perf_counter() - t0

        if not is_valid_tour(tour, instance.n):
            continue

        lengths.append(length)
        times.append(elapsed)

    if not lengths: return None

    best = min(lengths)
    avg = sum(lengths) / len(lengths)
    avg_time = sum(times) / len(times)

    # Gap vs NN
    gap_nn = 100 * (best - nn_len) / nn_len

    return {
        "instance": instance.name,
        "cities": instance.n,
        "random": r_best,
        "nn": nn_len,
        "best": best,
        "avg": avg,
        "gap_nn": gap_nn,
        "time": avg_time,
        "runs": n_runs
    }

def print_result_table(results: List[Dict]):
    print("\n" + "="*95)
    header = f"{'Instance':<10} | {'Cities':<6} | {'Rand Best':>10} | {'NN':>10} | {'Our Best':>10} | {'Gap/NN %':>9} | {'Time':>6}"
    print(header)
    print("-"*95)
    for r in results:
        print(f"{r['instance']:<10} | {r['cities']:<6} | {r['random']:>10.1f} | {r['nn']:>10.1f} | {r['best']:>10.2f} | {r['gap_nn']:>8.2f}% | {r['time']:>5.2f}s")
    print("="*95)

if __name__ == "__main__":
    from research.advanced_solvers import TSPSolver
    def wrap_solver(inst, max_iter, seed):
        s = TSPSolver(inst.name, inst.coords, seed=seed)
        return s.solve(max_iter=max_iter, init_method='nn', verbose=False) # NN + 2-opt

    instances = load_data("datasets/tsplib/tsp_instances_dataset.csv")
    results = []
    for inst in instances[:10]:
        res = run_evaluation(inst, wrap_solver, n_runs=10, max_iter=50000)
        if res: results.append(res)

    print_result_table(results)
