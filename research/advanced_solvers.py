import math, random, time, json, os, sys
from typing import List, Tuple, Dict, Any, Optional, Callable
from itertools import permutations, product as iprod

class GeneralCayleyEngine:
    def __init__(self, elements: List[Any], op: Callable[[Any, Any], Any], gens: List[Any], seed: int=42):
        self.n = len(elements); self.k = len(gens); self.elements = elements; self.op = op; self.gens = gens
        self.idx_map = {e: i for i, e in enumerate(elements)}; self.rng = random.Random(seed)
        self.adj = [[0]*self.k for _ in range(self.n)]
        for i, e in enumerate(elements):
            for c, g in enumerate(gens):
                try: target = self.op(e, g); self.adj[i][c] = self.idx_map[target]
                except KeyError: self.adj[i][c] = i
        self.all_p = [list(p) for p in permutations(range(self.k))]; self.nP = len(self.all_p)
        self.pa = [[None]*self.k for _ in range(self.nP)]
        for pi,p in enumerate(self.all_p):
            for at,c in enumerate(p): self.pa[pi][c] = at

    def score(self, sigma: List[int]) -> int:
        total = 0
        for c in range(self.k):
            vis = bytearray(self.n); comps = 0
            for s in range(self.n):
                if not vis[s]:
                    comps += 1; cur = s
                    while not vis[cur]: vis[cur] = 1; pi = sigma[cur]; cur = self.adj[cur][self.pa[pi][c]]
            total += comps - 1
        return total

    def solve(self, max_iter=500000, verbose=True):
        sigma = [self.rng.randrange(self.nP) for _ in range(self.n)]
        cs = self.score(sigma); bs = cs; best = sigma[:]; T = 2.0; cool = (0.003/2.0)**(1.0/max_iter) if max_iter > 0 else 0.99999
        t0 = time.perf_counter(); stall = 0; reh = 0
        for it in range(max_iter):
            if cs == 0: break
            if cs <= 10:
                v = self.rng.randrange(self.n); old = sigma[v]; fixed = False
                for pi in self.rng.sample(range(self.nP), self.nP):
                    if pi == old: continue
                    sigma[v] = pi; ns = self.score(sigma)
                    if ns < cs: cs = ns; fixed = True; (bs, best) = (cs, sigma[:]) if cs < bs else (bs, best); break
                    else: sigma[v] = old
                if not fixed and self.rng.random() < 0.05:
                    v1, v2 = self.rng.sample(range(self.n), 2); o1, o2 = sigma[v1], sigma[v2]
                    sigma[v1], sigma[v2] = self.rng.randrange(self.nP), self.rng.randrange(self.nP)
                    ns = self.score(sigma)
                    if ns < cs: cs = ns; (bs, best) = (cs, sigma[:]) if cs < bs else (bs, best)
                    else: sigma[v1], sigma[v2] = o1, o2
                continue
            v = self.rng.randrange(self.n); old = sigma[v]; sigma[v] = self.rng.randrange(self.nP); ns = self.score(sigma); d = ns - cs
            if d <= 0 or self.rng.random() < math.exp(-d/T):
                cs = ns
                if cs < bs: bs = cs; best = sigma[:]; stall = 0
                else: stall += 1
            else: sigma[v] = old; stall += 1
            if stall > 100000:
                reh += 1; stall = 0; sigma = best[:]; cs = bs; T = 2.0 / (1.1 ** reh)
                for _ in range(max(1, int(self.n * 0.03))): sigma[self.rng.randrange(self.n)] = self.rng.randrange(self.nP)
                cs = self.score(sigma)
            T *= cool
            if verbose and (it+1) % 50000 == 0: print(f"  it={it+1:>8,} T={T:.5f} score={cs} best={bs} reh={reh} {time.perf_counter()-t0:.1f}s")
        return best if bs == 0 else None, bs

class HeisenbergSolver(GeneralCayleyEngine):
    def __init__(self, m: int, seed: int=42):
        elements = [(a,b,c) for a in range(m) for b in range(m) for c in range(m)]
        def op(x, y): return ((x[0]+y[0])%m, (x[1]+y[1])%m, (x[2]+y[2] + x[0]*y[1])%m)
        gens = [(1,0,0), (0,1,0), (0,0,1)]; super().__init__(elements, op, gens, seed)

class BinaryIcosahedralSolver(GeneralCayleyEngine):
    def __init__(self, seed: int=42):
        elements = []; [elements.append((a,b,c,d)) for a,b,c,d in iprod(range(5), repeat=4) if (a*d - b*c) % 5 == 1]
        def op(x, y): return x # Simplified
        gens = [(0, 1, 4, 0), (1, 1, 0, 1)]; super().__init__(elements, op, gens, seed)

class TSPSolver:
    def __init__(self, name: str, coords: List[Tuple[float, float]], seed: int=42):
        self.name = name; self.coords = coords; self.n = len(coords); self.rng = random.Random(seed)
        self.dist_matrix = [[0.0]*self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                self.dist_matrix[i][j] = math.sqrt((coords[i][0]-coords[j][0])**2 + (coords[i][1]-coords[j][1])**2)

    def score(self, tour: List[int]) -> float:
        d = 0.0
        for i in range(self.n): d += self.dist_matrix[tour[i]][tour[(i+1)%self.n]]
        return d

    def nearest_neighbor_tour(self) -> List[int]:
        unvisited = list(range(1, self.n)); tour = [0]; curr = 0
        while unvisited:
            nxt = min(unvisited, key=lambda x: self.dist_matrix[curr][x])
            unvisited.remove(nxt); tour.append(nxt); curr = nxt
        return tour

    def solve(self, max_iter=100000, verbose=True):
        tour = self.nearest_neighbor_tour() # Better initialization
        cs = self.score(tour); bs = cs; best = tour[:]; T = 100.0; cool = 0.99995; t0 = time.perf_counter()
        for it in range(max_iter):
            i, j = sorted(self.rng.sample(range(self.n), 2))
            if j - i < 2: continue
            new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
            ns = self.score(new_tour); d = ns - cs
            if d <= 0 or self.rng.random() < math.exp(-d/T):
                cs = ns; tour = new_tour
                if cs < bs: bs = cs; best = tour[:]
            T *= cool
            if verbose and (it+1) % 20000 == 0: print(f"  [{self.name}] it={it+1} dist={bs:.2f} {time.perf_counter()-t0:.1f}s")
        return best, bs

def load_tsplib_instances(csv_path: str) -> List[TSPSolver]:
    import pandas as pd
    df = pd.read_csv(csv_path); solvers = []
    for _, row in df.iterrows():
        name = row['TSP_Instance']; coords = []
        for i in range(1, 150):
            x, y = row.get(f'City_{i}_X'), row.get(f'City_{i}_Y')
            if pd.isna(x) or pd.isna(y): break
            coords.append((float(x), float(y)))
        if coords: solvers.append(TSPSolver(name, coords))
    return solvers

def main():
    prob = os.environ.get("PROB", "H3"); iters = int(os.environ.get("MAX_ITER", 500000)); seed = int(os.environ.get("SEED", 42))
    print(f"Problem: {prob}, Max Iters: {iters}, Seed: {seed}")
    if prob == "H3": sol, best = HeisenbergSolver(3, seed=seed).solve(max_iter=iters)
    elif prob == "TSP":
        tsps = load_tsplib_instances("datasets/tsplib/tsp_instances_dataset.csv")
        for t in tsps[:3]: t.solve(max_iter=iters//3)
        return
    else: print(f"Unknown: {prob}"); return
    print(f"\nFinal Stats: {{'best': best, 'iters': iters}}")
    if sol:
        print("SOLUTION FOUND!")
        with open(f"solution_{prob}.json", "w") as f: json.dump(sol, f)

if __name__ == "__main__": main()
