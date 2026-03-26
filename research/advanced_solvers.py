import math, random, time, json
from typing import List, Tuple, Dict, Any, Callable
from itertools import permutations, product as iprod

class GeneralCayleyEngine:
    """
    Advanced Basin Escape v3.2 for general Cayley graphs.
    """
    def __init__(self, elements: List[Any], op: Callable[[Any, Any], Any], gens: List[Any], seed: int=42):
        self.n = len(elements)
        self.k = len(gens)
        self.elements = elements
        self.op = op
        self.gens = gens
        self.idx_map = {e: i for i, e in enumerate(elements)}
        self.rng = random.Random(seed)

        self.adj = [[0]*self.k for _ in range(self.n)]
        for i, e in enumerate(elements):
            for c, g in enumerate(gens):
                self.adj[i][c] = self.idx_map[self.op(e, g)]

        self.all_p = [list(p) for p in permutations(range(self.k))]
        self.nP = len(self.all_p)
        self.pa = [[None]*self.k for _ in range(self.nP)]
        for pi,p in enumerate(self.all_p):
            for at,c in enumerate(p):
                self.pa[pi][c] = at

    def score(self, sigma: List[int]) -> int:
        total = 0
        for c in range(self.k):
            vis = bytearray(self.n)
            comps = 0
            for s in range(self.n):
                if not vis[s]:
                    comps += 1
                    cur = s
                    while not vis[cur]:
                        vis[cur] = 1
                        pi = sigma[cur]
                        cur = self.adj[cur][self.pa[pi][c]]
            total += comps - 1
        return total

    def solve(self, max_iter=500_000, verbose=True):
        sigma = [self.rng.randrange(self.nP) for _ in range(self.n)]
        cs = self.score(sigma)
        bs = cs
        best = sigma[:]

        T = 2.0
        cool = 0.99999
        t0 = time.perf_counter()
        stall = 0
        reheats = 0

        for it in range(max_iter):
            if cs == 0: break

            # Basin Escape v3.2: Deep Greedy for low scores
            if cs <= 10:
                v = self.rng.randrange(self.n)
                old = sigma[v]
                fixed = False
                for pi in self.rng.sample(range(self.nP), self.nP):
                    if pi == old: continue
                    sigma[v] = pi
                    ns = self.score(sigma)
                    if ns < cs:
                        cs = ns
                        if cs < bs: bs = cs; best = sigma[:]
                        fixed = True; break
                    else:
                        sigma[v] = old
                if not fixed and self.rng.random() < 0.05:
                    # Try a 2-node random swap
                    v1, v2 = self.rng.sample(range(self.n), 2)
                    o1, o2 = sigma[v1], sigma[v2]
                    sigma[v1], sigma[v2] = self.rng.randrange(self.nP), self.rng.randrange(self.nP)
                    ns = self.score(sigma)
                    if ns < cs:
                        cs = ns
                        if cs < bs: bs = cs; best = sigma[:]
                    else:
                        sigma[v1], sigma[v2] = o1, o2
                continue

            # Standard SA move
            v = self.rng.randrange(self.n)
            old = sigma[v]
            sigma[v] = self.rng.randrange(self.nP)
            ns = self.score(sigma)
            d = ns - cs

            if d <= 0 or self.rng.random() < math.exp(-d/T):
                cs = ns
                if cs < bs:
                    bs = cs
                    best = sigma[:]
                    stall = 0
                else:
                    stall += 1
            else:
                sigma[v] = old
                stall += 1

            if stall > 50_000:
                reheats += 1
                stall = 0
                sigma = best[:]
                cs = bs
                T = 2.0 / (1.1 ** reheats)
                for _ in range(max(1, int(self.n * 0.03))):
                    sigma[self.rng.randrange(self.n)] = self.rng.randrange(self.nP)
                cs = self.score(sigma)

            T *= cool
            if verbose and (it+1) % 50_000 == 0:
                print(f"  it={it+1:>8,} T={T:.5f} score={cs} best={bs} reh={reheats} {time.perf_counter()-t0:.1f}s")

        return best if bs == 0 else None, bs

class HeisenbergSolver(GeneralCayleyEngine):
    def __init__(self, m: int, seed: int=42):
        elements = [(a,b,c) for a in range(m) for b in range(m) for c in range(m)]
        def op(x, y):
            a1, b1, c1 = x; a2, b2, c2 = y
            return ((a1+a2)%m, (b1+b2)%m, (c1+c2 + a1*b2)%m)
        gens = [(1,0,0), (0,1,0), (0,0,1)]
        super().__init__(elements, op, gens, seed)

class BinaryIcosahedralSolver(GeneralCayleyEngine):
    def __init__(self, seed: int=42):
        elements = []
        for a,b,c,d in iprod(range(5), repeat=4):
            if (a*d - b*c) % 5 == 1: elements.append((a,b,c,d))
        def op(x, y):
            a1, b1, c1, d1 = x; a2, b2, c2, d2 = y
            return ((a1*a2 + b1*c2)%5, (a1*b2 + b1*d2)%5, (c1*a2 + d1*c2)%5, (c1*b2 + d1*d2)%5)
        S = (0, 1, 4, 0); T = (1, 1, 0, 1)
        gens = [S, T, op(S, T)]
        super().__init__(elements, op, gens, seed)

if __name__ == "__main__":
    import sys
    prob = sys.argv[1] if len(sys.argv) > 1 else "H3"
    if prob == "H3":
        sol, best = HeisenbergSolver(3).solve()
    else:
        sol, best = BinaryIcosahedralSolver().solve()
    print(f"Result: {prob} Best={best}")
