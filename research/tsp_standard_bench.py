import math, random, time, sys
from typing import List, Tuple, Dict

def parse_tsp(file_path):
    coords = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        section = None
        for line in lines:
            line = line.strip()
            if line.startswith("DISPLAY_DATA_SECTION") or line.startswith("NODE_COORD_SECTION"):
                section = "COORDS"; continue
            if line.startswith("EOF") or line.startswith("EDGE_WEIGHT_SECTION"): section = None
            if section == "COORDS":
                parts = line.split()
                if len(parts) >= 3:
                    coords.append((float(parts[1]), float(parts[2])))
    return coords

def solve_nn(coords):
    n = len(coords)
    dist = lambda i, j: math.sqrt((coords[i][0]-coords[j][0])**2 + (coords[i][1]-coords[j][1])**2)
    unvisited = list(range(1, n)); tour = [0]; curr = 0; total = 0
    while unvisited:
        nxt = min(unvisited, key=lambda x: dist(curr, x))
        total += dist(curr, nxt); unvisited.remove(nxt); tour.append(nxt); curr = nxt
    total += dist(curr, 0)
    return tour, total

def solve_2opt(coords, max_iter=50000, seed=42):
    n = len(coords); rng = random.Random(seed)
    dist_matrix = [[math.sqrt((coords[i][0]-coords[j][0])**2 + (coords[i][1]-coords[j][1])**2) for j in range(n)] for i in range(n)]
    tour, cs = solve_nn(coords); bs = cs; best = tour[:]
    T = 100.0; cool = 0.99995
    for it in range(max_iter):
        i, j = sorted(rng.sample(range(n), 2))
        if j - i < 2: continue
        new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
        ns = 0
        # Only check changed edges
        a, b = tour[i], tour[i+1]
        c, d = tour[j], tour[(j+1)%n]
        ns = cs - dist_matrix[a][b] - dist_matrix[c][d] + dist_matrix[a][c] + dist_matrix[b][d]
        if ns < cs:
            cs = ns; tour = new_tour
            if cs < bs: bs = cs; best = tour[:]
    return best, bs

# Optimal values from TSPLIB
OPTIMALS = {"bayg29": 1610, "eil51": 426, "st70": 675}

def run():
    files = [("bayg29", "datasets/tsplib_real/tsp_dataset/bayg29.tsp"),
             ("eil51", "datasets/tsplib_real/tsp_dataset/eil51.tsp"),
             ("st70", "datasets/tsplib_real/tsp_dataset/st70.tsp")]

    print(f"{'Instance':<10} | {'Cities':<6} | {'Best':>10} | {'Known':>10} | {'Gap %':>8} | {'Time':>6}")
    print("-" * 65)
    for name, path in files:
        coords = parse_tsp(path)
        t0 = time.perf_counter()
        best_tour, best_len = solve_2opt(coords, max_iter=100000)
        elapsed = time.perf_counter() - t0
        known = OPTIMALS[name]
        gap = 100 * (best_len - known) / known
        print(f"{name:<10} | {len(coords):<6} | {best_len:>10.2f} | {known:>10.2f} | {gap:>7.2f}% | {elapsed:>5.2f}s")

if __name__ == "__main__":
    run()
