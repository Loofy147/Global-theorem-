"""
search.py — Three complementary search strategies for Claude's Cycles.

1. RANDOM SEARCH: Fast for odd m. Sample random valid-level combinations,
   check if Q compositions are single m²-cycles. Works well for m=3,5,7.

2. BACKTRACKING: Vertex-by-vertex with in-degree pruning. Explores the full
   sigma space (not restricted to column-uniform). Slower but more general.

3. SIMULATED ANNEALING: Continuous improvement via stochastic hill-climbing.
   Score = total "extra components" across 3 cycles (want 0).
   Effective at navigating large m.

All strategies return a SigmaTable (for fiber-based) or SigmaFn (for full 3D).
"""

from __future__ import annotations
import random, math, time
from typing import Optional, List, Tuple, Callable, Dict
from itertools import permutations as _iperms, product as _product

from .core import (
    Vertex, Perm, SigmaFn, FuncGraph, ARC_SHIFTS,
    build_functional_graphs, verify_functional_graph, vertices
)
from .fiber import (
    SigmaTable, LevelTable, all_valid_levels,
    compose_levels, is_single_q_cycle, table_to_sigma_fn
)

_ALL_PERMS: List[Perm] = [list(p) for p in _iperms(range(3))]


# =========================================================================== #
# 1. RANDOM SEARCH (fiber-based, column-uniform sigma)
# =========================================================================== #

class RandomSearch:
    """
    Sample random combinations of valid level tables.
    Extremely fast for odd m. Progressively slows for large m.

    Usage:
        rs = RandomSearch(m=5)
        result = rs.run(max_attempts=50_000)
    """

    def __init__(self, m: int, seed: Optional[int] = None):
        self.m = m
        self.rng = random.Random(seed)
        self.valid_levels: List[LevelTable] = all_valid_levels(m)
        self._attempts = 0
        self._elapsed = 0.0

    @property
    def attempts(self) -> int:
        return self._attempts

    @property
    def elapsed(self) -> float:
        return self._elapsed

    def run(self, max_attempts: int = 100_000) -> Optional[SigmaTable]:
        """Return a valid SigmaTable or None if not found."""
        m = self.m
        t0 = time.perf_counter()
        for attempt in range(max_attempts):
            self._attempts = attempt + 1
            table = [self.rng.choice(self.valid_levels) for _ in range(m)]
            Qs = compose_levels(table, m)
            if all(is_single_q_cycle(Q, m) for Q in Qs):
                self._elapsed = time.perf_counter() - t0
                return table
        self._elapsed = time.perf_counter() - t0
        return None

    def run_verbose(self, max_attempts: int = 100_000,
                    report_every: int = 10_000) -> Optional[SigmaTable]:
        """Like run() but prints progress."""
        m = self.m
        print(f"RandomSearch m={m}: {len(self.valid_levels)} valid levels, "
              f"up to {max_attempts:,} attempts")
        t0 = time.perf_counter()
        for attempt in range(max_attempts):
            self._attempts = attempt + 1
            table = [self.rng.choice(self.valid_levels) for _ in range(m)]
            Qs = compose_levels(table, m)
            if all(is_single_q_cycle(Q, m) for Q in Qs):
                self._elapsed = time.perf_counter() - t0
                print(f"  ✅ Found at attempt {attempt+1} ({self._elapsed:.3f}s)")
                return table
            if (attempt+1) % report_every == 0:
                print(f"  ... {attempt+1:,} attempts, {time.perf_counter()-t0:.1f}s elapsed")
        self._elapsed = time.perf_counter() - t0
        print(f"  ❌ Not found in {max_attempts:,} attempts ({self._elapsed:.1f}s)")
        return None


# =========================================================================== #
# 2. BACKTRACKING SEARCH (full 3D sigma, in-degree pruning)
# =========================================================================== #

class BacktrackSearch:
    """
    Vertex-by-vertex assignment of sigma with pruning:
    - Each cycle gets exactly one arc from each vertex (permutation = guaranteed).
    - Each vertex has in-degree exactly 1 per cycle (checked incrementally).
    - Optionally shuffles perm order (via seed) for different search trees.

    Usage:
        bt = BacktrackSearch(m=3, seed=42)
        sigma_fn = bt.run()
    """

    def __init__(self, m: int, seed: Optional[int] = None):
        self.m = m
        self.rng = random.Random(seed)
        self._nodes = 0
        self._elapsed = 0.0

    @property
    def nodes_visited(self) -> int:
        return self._nodes

    def run(self) -> Optional[SigmaFn]:
        """Return SigmaFn or None."""
        m = self.m
        verts = vertices(m)
        n = m**3
        sigma: Dict[Vertex, Perm] = {}
        funcs: List[FuncGraph] = [{}, {}, {}]
        in_deg: List[Dict[Vertex, int]] = [{}, {}, {}]
        t0 = time.perf_counter()
        self._nodes = 0

        def _bt(idx: int) -> bool:
            if idx == n:
                # Final single-cycle check
                for fg in funcs:
                    ok, _ = verify_functional_graph(fg, m)
                    if not ok:
                        return False
                return True

            v = verts[idx]
            neighbors = [
                tuple((v[d] + ARC_SHIFTS[at][d]) % m for d in range(3))
                for at in range(3)
            ]
            perms = _ALL_PERMS[:]
            self.rng.shuffle(perms)

            for perm in perms:
                self._nodes += 1
                # In-degree check
                conflict = any(in_deg[perm[at]].get(neighbors[at], 0) >= 1
                               for at in range(3))
                if conflict:
                    continue
                # Assign
                sigma[v] = perm
                for at, c in enumerate(perm):
                    funcs[c][v] = neighbors[at]
                    in_deg[c][neighbors[at]] = in_deg[c].get(neighbors[at], 0) + 1
                # Recurse
                if _bt(idx + 1):
                    self._elapsed = time.perf_counter() - t0
                    return True
                # Undo
                del sigma[v]
                for at, c in enumerate(perm):
                    del funcs[c][v]
                    in_deg[c][neighbors[at]] -= 1
                    if in_deg[c][neighbors[at]] == 0:
                        del in_deg[c][neighbors[at]]
            return False

        found = _bt(0)
        self._elapsed = time.perf_counter() - t0
        if not found:
            return None

        # Capture sigma as a closure
        captured = dict(sigma)
        def sigma_fn(i: int, j: int, k: int) -> Perm:
            return list(captured[(i, j, k)])
        return sigma_fn


# =========================================================================== #
# 3. SIMULATED ANNEALING (full 3D sigma)
# =========================================================================== #

class SimulatedAnnealing:
    """
    Score = total number of extra cycle components (want 0).
    Perturb: change sigma at one random vertex.
    Temperature schedule: geometric cooling.

    Usage:
        sa = SimulatedAnnealing(m=4, seed=0)
        sigma_fn = sa.run(max_iter=500_000)
    """

    def __init__(self, m: int, seed: Optional[int] = None,
                 T_init: float = 3.0, T_min: float = 0.01):
        self.m = m
        self.rng = random.Random(seed)
        self.T_init = T_init
        self.T_min = T_min
        self._best_score = float("inf")
        self._elapsed = 0.0

    @property
    def best_score(self) -> float:
        return self._best_score

    def _score(self, funcs: List[FuncGraph], m: int) -> int:
        """Sum of extra components (0 = perfect)."""
        total = 0
        for fg in funcs:
            visited: set = set()
            comps = 0
            for start in fg:
                if start not in visited:
                    comps += 1
                    cur = start
                    while cur not in visited:
                        visited.add(cur)
                        cur = fg[cur]
            total += comps - 1  # each component beyond 1 is a violation
        return total

    def run(self, max_iter: int = 500_000,
            verbose: bool = False,
            report_every: int = 50_000) -> Optional[SigmaFn]:
        m = self.m
        rng = self.rng
        verts = vertices(m)
        n = m**3

        # Initialize randomly
        sigma = {v: list(rng.choice(_ALL_PERMS)) for v in verts}
        funcs = build_functional_graphs(lambda i,j,k: sigma[(i,j,k)], m)
        current_score = self._score(funcs, m)
        best_score = current_score
        best_sigma = {v: list(p) for v, p in sigma.items()}

        cool = (self.T_min / self.T_init) ** (1.0 / max_iter)
        T = self.T_init
        t0 = time.perf_counter()

        for it in range(max_iter):
            if current_score == 0:
                break
            v = rng.choice(verts)
            old_perm = sigma[v][:]
            sigma[v] = list(rng.choice(_ALL_PERMS))

            new_funcs = build_functional_graphs(lambda i,j,k: sigma[(i,j,k)], m)
            new_score = self._score(new_funcs, m)
            delta = new_score - current_score

            if delta < 0 or rng.random() < math.exp(-delta / T):
                funcs = new_funcs
                current_score = new_score
                if current_score < best_score:
                    best_score = current_score
                    best_sigma = {v: list(p) for v, p in sigma.items()}
            else:
                sigma[v] = old_perm

            T *= cool
            if verbose and (it + 1) % report_every == 0:
                print(f"  SA iter={it+1:>8,}  T={T:.4f}  "
                      f"score={current_score}  best={best_score}")

        self._best_score = best_score
        self._elapsed = time.perf_counter() - t0

        if best_score > 0:
            return None

        captured = {v: list(p) for v, p in best_sigma.items()}
        def sigma_fn(i: int, j: int, k: int) -> Perm:
            return list(captured[(i, j, k)])
        return sigma_fn

    def run_verbose(self, max_iter: int = 500_000) -> Optional[SigmaFn]:
        print(f"SimulatedAnnealing m={self.m}  max_iter={max_iter:,}  "
              f"T={self.T_init}→{self.T_min}")
        result = self.run(max_iter=max_iter, verbose=True, report_every=50_000)
        if result:
            print(f"  ✅ Found!  elapsed={self._elapsed:.1f}s")
        else:
            print(f"  ❌ Best score={self._best_score}  elapsed={self._elapsed:.1f}s")
        return result


# =========================================================================== #
# Unified search interface
# =========================================================================== #

def find_sigma(m: int,
               strategy: str = "auto",
               seed: Optional[int] = None,
               max_iter: int = 200_000,
               verbose: bool = False) -> Optional[SigmaFn]:
    """
    Find a valid sigma for the given m using the best available strategy.

    strategy="auto":
      - odd m  → RandomSearch (fast, fiber-based)
      - even m → SimulatedAnnealing (full 3D)
    strategy="random"    → RandomSearch only
    strategy="backtrack" → BacktrackSearch only
    strategy="sa"        → SimulatedAnnealing only

    Returns SigmaFn or None.
    """
    if strategy == "auto":
        strategy = "random" if m % 2 == 1 else "sa"

    if strategy == "random":
        rs = RandomSearch(m, seed=seed)
        table = (rs.run_verbose(max_iter) if verbose else rs.run(max_iter))
        if table is None:
            return None
        return table_to_sigma_fn(table, m)

    elif strategy == "backtrack":
        bt = BacktrackSearch(m, seed=seed)
        return bt.run()

    elif strategy == "sa":
        sa = SimulatedAnnealing(m, seed=seed)
        return (sa.run_verbose(max_iter) if verbose else sa.run(max_iter))

    else:
        raise ValueError(f"Unknown strategy: {strategy!r}. "
                         "Choose 'auto', 'random', 'backtrack', or 'sa'.")
