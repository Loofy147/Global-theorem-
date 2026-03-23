"""
Santa 2025: Hamiltonian Decomposition Framework (Draft)
Goal: Decompose a complete graph (or a dense symmetric graph) into disjoint Hamiltonian cycles.
"""

import math, random
from typing import List, Tuple, Dict

class SantaOptimizer:
    def __init__(self, n_cities: int, m_cycles: int):
        self.n = n_cities
        self.m = m_cycles
        # Representation: m Hamiltonian cycles
        # Each cycle is a permutation of range(n)
        self.cycles = [list(range(self.n)) for _ in range(self.m)]
        for c in self.cycles: random.shuffle(c)

    def score(self) -> int:
        """
        Total weight of all m cycles.
        In SES framework, we want disjointness (score = number of shared edges).
        """
        edges = set()
        shared = 0
        for c in self.cycles:
            for i in range(self.n):
                e = tuple(sorted((c[i], c[(i+1)%self.n])))
                if e in edges:
                    shared += 1
                edges.add(e)
        return shared

    def step(self):
        """Standard 2-opt move on a random cycle."""
        c_idx = random.randrange(self.m)
        c = self.cycles[c_idx]
        i, j = sorted(random.sample(range(self.n), 2))
        # Reverse segment [i, j]
        c[i:j] = reversed(c[i:j])

    def solve(self, max_iter=100_000):
        cs = self.score()
        for it in range(max_iter):
            if cs == 0: break
            # Try a move
            c_idx = random.randrange(self.m)
            c = self.cycles[c_idx]
            i, j = sorted(random.sample(range(self.n), 2))
            old_seg = c[i:j]
            c[i:j] = reversed(old_seg)
            ns = self.score()
            if ns <= cs:
                cs = ns
            else:
                c[i:j] = old_seg
            if it % 10_000 == 0:
                print(f"Iteration {it}, Shared Edges: {cs}")
        return cs

if __name__ == "__main__":
    # Test on a small instance: 10 cities, 2 Hamiltonian cycles
    opt = SantaOptimizer(10, 2)
    print(f"Initial Score: {opt.score()}")
    final = opt.solve()
    print(f"Final Score: {final}")
