"""
Santa 2025: Hamiltonian Decomposition Framework (v2.2 Basin Escape)
Goal: Decompose a complete graph into disjoint Hamiltonian cycles.
"""

import math, random
from typing import List, Tuple, Dict

class SantaOptimizer:
    def __init__(self, n_cities: int, m_cycles: int, seed: int = 42):
        self.n = n_cities
        self.m = m_cycles
        self.rng = random.Random(seed)
        self.cycles = [list(range(self.n)) for _ in range(self.m)]
        for c in self.cycles: self.rng.shuffle(c)

    def score(self) -> int:
        edges = set()
        shared = 0
        for c in self.cycles:
            for i in range(self.n):
                e = tuple(sorted((c[i], c[(i+1)%self.n])))
                if e in edges: shared += 1
                edges.add(e)
        return shared

    def solve(self, max_iter=100_000):
        cs = self.score(); bs = cs; best_cycles = [c[:] for c in self.cycles]
        T = 2.0; cool = 0.9999

        for it in range(max_iter):
            if cs == 0: break

            # Basin Escape v2.2 logic for Santa
            if cs <= 5:
                # Greedy orbit/cycle-merging move
                c_idx = self.rng.randrange(self.m)
                old_c = self.cycles[c_idx][:]
                i, j = sorted(self.rng.sample(range(self.n), 2))
                self.cycles[c_idx][i:j] = reversed(self.cycles[c_idx][i:j])
                ns = self.score()
                if ns < cs:
                    cs = ns
                    if cs < bs: bs = cs; best_cycles = [c[:] for c in self.cycles]
                else:
                    self.cycles[c_idx] = old_c
                continue

            c_idx = self.rng.randrange(self.m)
            old_c = self.cycles[c_idx][:]
            i, j = sorted(self.rng.sample(range(self.n), 2))
            self.cycles[c_idx][i:j] = reversed(self.cycles[c_idx][i:j])
            ns = self.score(); d = ns - cs
            if d <= 0 or self.rng.random() < math.exp(-d / T):
                cs = ns
                if cs < bs: bs = cs; best_cycles = [c[:] for c in self.cycles]
            else:
                self.cycles[c_idx] = old_c
            T *= cool

        self.cycles = best_cycles
        return bs

if __name__ == "__main__":
    opt = SantaOptimizer(20, 3)
    print(f"Initial Shared: {opt.score()}")
    final = opt.solve(max_iter=50_000)
    print(f"Final Shared: {final}")
