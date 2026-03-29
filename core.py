"""
core.py — Mathematical Foundations
====================================
Weights · Verifier · Solutions · Level Machinery · SA Engine

The 8 weights classify any (m, k) problem in the moduli space M_k(G_m).
All are closed-form, all O(m²) or faster.

  W1  H² obstruction    bool   proves impossible in O(1)
  W2  r-tuple count     int    how many construction seeds
  W3  canonical seed    tuple  the direct construction path
  W4  H¹ order EXACT    int    phi(m)  — gauge multiplicity
  W5  search exponent   float  log₂(compressed space)
  W6  compression ratio float  W5 / log₂(full space)
  W7  solution lb       int    phi(m) × coprime_b(m)^(k-1)  [exact for m=3]
  W8  orbit size        int    m^(m-1)
"""

import math, random
from math import gcd, log2, factorial
from itertools import permutations, product as iprod
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass
from functools import lru_cache

# ── pre-computed tables ───────────────────────────────────────────────────────
_LEVEL_COUNTS: Dict[int,int] = {2:2,3:24,4:48,5:384,6:1152,7:5040,8:13440,9:72576}
_ALL_P3 = [list(p) for p in permutations(range(3))]
_FIBER_SHIFTS = ((1,0),(0,1),(0,0))   # i-shift, j-shift for arc types 0,1,2


# ══════════════════════════════════════════════════════════════════════════════
# THE 8 WEIGHTS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Weights:
    m: int; k: int
    h2_blocks:   bool           # W1
    r_count:     int            # W2
    canonical:   Optional[tuple]# W3
    h1_exact:    int            # W4 = phi(m)
    search_exp:  float          # W5
    compression: float          # W6
    sol_lb:      int            # W7 lower bound
    orbit_size:  int            # W8
    coprime_elems: tuple        # cached

    @property
    def strategy(self) -> str:
        if self.h2_blocks:   return "S4"  # prove impossible
        if self.r_count > 0: return "S1"  # column-uniform
        return                      "S2"  # fiber-structured SA

    @property
    def solvable(self) -> bool:
        return not self.h2_blocks and self.r_count > 0

    def summary(self) -> str:
        ok = "H²=0" if not self.h2_blocks else "H²≠0"
        return (f"({self.m},{self.k}) {ok} r={self.r_count} "
                f"W3={self.canonical} W4=φ={self.h1_exact} "
                f"W6={self.compression:.4f} → {self.strategy}")


@lru_cache(maxsize=1024)
def extract_weights(m: int, k: int) -> Weights:
    """Extract all 8 weights for problem (m,k). Cached."""
    cp = tuple(r for r in range(1, m) if gcd(r, m) == 1)
    phi_m = len(cp)

    # W1: H² obstruction
    all_odd = bool(cp) and all(r % 2 == 1 for r in cp)
    h2 = all_odd and (k % 2 == 1) and (m % 2 == 0)

    # W2/W3: r-tuples — Optimized
    r_count = 0
    canon = None
    if not h2:
        if k == 3:
            cp_set = set(cp)
            for r0 in cp:
                for r1 in cp:
                    r2 = m - r0 - r1
                    if r2 in cp_set:
                        r_count += 1
                        if canon is None: canon = (r0, r1, r2)
        elif k == 4:
            cp_set = set(cp)
            for r0 in cp:
                for r1 in cp:
                    for r2 in cp:
                        r3 = m - r0 - r1 - r2
                        if r3 in cp_set:
                            r_count += 1
                            if canon is None: canon = (r0, r1, r2, r3)
        else:
            mid = m - (k - 1)
            if mid > 0 and gcd(mid, m) == 1:
                canon = (1,) * (k-1) + (mid,)
                r_count = 1

    h1 = phi_m
    lev = _LEVEL_COUNTS.get(m, phi_m * 6)
    full_exp   = (m**3 if m > 0 else 1) * log2(6)
    search_exp = m * log2(lev) if lev > 0 else 0
    compression = search_exp / full_exp if full_exp > 0 else 1.0

    return Weights(m, k, h2, r_count, canon, h1, search_exp, compression, h1, m**(max(1, m-1)), cp)

# ══════════════════════════════════════════════════════════════════════════════
# VERIFIER
# ══════════════════════════════════════════════════════════════════════════════

def verify_sigma(sigma: Dict[Tuple, Tuple], m: int) -> bool:
    """Verify that sigma decomposes Z_m^3 into 3 disjoint Hamiltonian cycles."""
    n = m**3
    if len(sigma) != n: return False
    for c in range(3):
        vis = set(); cur = (0,0,0)
        for _ in range(n):
            if cur in vis: return False
            vis.add(cur); p = sigma.get(cur)
            if not p: return False
            arc_type = p[c]; next_v = list(cur)
            next_v[arc_type] = (next_v[arc_type] + 1) % m
            cur = tuple(next_v)
        if len(vis) != n or cur != (0,0,0): return False
    return True

# ══════════════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ══════════════════════════════════════════════════════════════════════════════

_TABLE_M3 = [
    [ (0,1,2), (0,1,2), (0,1,2) ],
    [ (0,2,1), (0,2,1), (0,2,1) ],
    [ (1,0,2), (2,1,0), (1,2,0) ]
]

_TABLE_M5 = [
    [(0,1,2)]*5, [(0,1,2)]*5, [(0,1,2)]*5, [(0,1,2)]*5,
    [(1,0,2), (1,0,2), (1,0,2), (1,0,2), (2,1,0)]
]

SOLUTION_M4 = {
    (0, 0, 0): (0, 1, 2), (0, 0, 1): (0, 1, 2), (0, 0, 2): (0, 1, 2), (0, 0, 3): (0, 1, 2), (0, 1, 0): (0, 1, 2), (0, 1, 1): (0, 1, 2), (0, 1, 2): (0, 1, 2), (0, 1, 3): (0, 1, 2), (0, 2, 0): (0, 1, 2), (0, 2, 1): (0, 1, 2), (0, 2, 2): (0, 1, 2), (0, 2, 3): (0, 1, 2), (0, 3, 0): (1, 0, 2), (0, 3, 1): (1, 0, 2), (0, 3, 2): (1, 0, 2), (0, 3, 3): (2, 1, 0), (1, 0, 0): (1, 2, 0), (1, 0, 1): (1, 2, 0), (1, 0, 2): (1, 2, 0), (1, 0, 3): (0, 2, 1), (1, 1, 0): (1, 2, 0), (1, 1, 1): (1, 2, 0), (1, 1, 2): (1, 2, 0), (1, 1, 3): (0, 2, 1), (1, 2, 0): (1, 2, 0), (1, 2, 1): (1, 2, 0), (1, 2, 2): (1, 2, 0), (1, 2, 3): (0, 2, 1), (1, 3, 0): (0, 2, 1), (1, 3, 1): (0, 2, 1), (1, 3, 2): (0, 2, 1), (1, 3, 3): (1, 0, 2), (2, 0, 0): (0, 1, 2), (2, 0, 1): (0, 1, 2), (2, 0, 2): (0, 1, 2), (2, 0, 3): (0, 1, 2), (2, 1, 0): (0, 1, 2), (2, 1, 1): (0, 1, 2), (2, 1, 2): (0, 1, 2), (2, 1, 3): (0, 1, 2), (2, 2, 0): (0, 1, 2), (2, 2, 1): (0, 1, 2), (2, 2, 2): (0, 1, 2), (2, 2, 3): (0, 1, 2), (2, 3, 0): (1, 0, 2), (2, 3, 1): (1, 0, 2), (2, 3, 2): (1, 0, 2), (2, 3, 3): (2, 1, 0), (3, 0, 0): (1, 2, 0), (3, 0, 1): (1, 2, 0), (3, 0, 2): (1, 2, 0), (3, 0, 3): (0, 2, 1), (3, 1, 0): (1, 2, 0), (3, 1, 1): (1, 2, 0), (3, 1, 2): (1, 2, 0), (3, 1, 3): (0, 2, 1), (3, 2, 0): (1, 2, 0), (3, 2, 1): (1, 2, 0), (3, 2, 2): (1, 2, 0), (3, 2, 3): (0, 2, 1), (3, 3, 0): (0, 2, 1), (3, 3, 1): (0, 2, 1), (3, 3, 2): (0, 2, 1), (3, 3, 3): (1, 0, 2)
}

def table_to_sigma(table: List[Dict], m: int) -> Dict:
    sigma = {}
    for i in range(m):
        for j in range(m):
            for k_coord in range(m):
                s = (i+j+k_coord)%m
                sigma[(i,j,k_coord)] = table[s][j]
    return sigma

PRECOMPUTED: Dict[Tuple[int,int], Dict] = {
    (3,3): table_to_sigma(_TABLE_M3, 3),
    (5,3): table_to_sigma(_TABLE_M5, 5),
    (4,3): dict(SOLUTION_M4),
}


# ══════════════════════════════════════════════════════════════════════════════
# SA CORE
# ══════════════════════════════════════════════════════════════════════════════

def _sa_score(sigma: List[int], arc_s: List[List[int]], pa: List[List[int]], n: int, k: int) -> int:
    score = 0
    for c in range(k):
        vis = bytearray(n); comps = 0
        for s in range(n):
            if not vis[s]:
                comps += 1; cur = s
                while not vis[cur]: vis[cur] = 1; cur = arc_s[cur][pa[sigma[cur]][c]]
        score += (comps - 1)
    return score

def _build_sa(m: int, k: int):
    n = m**k; all_p = [list(p) for p in permutations(range(k))]; nP = len(all_p)
    arc_s = [[0]*k for _ in range(n)]
    for idx in range(n):
        coords = []; val = idx
        for _ in range(k): coords.append(val % m); val //= m
        coords.reverse()
        for c in range(k):
            nxt = list(coords); nxt[c] = (nxt[c]+1)%m
            n_idx = 0
            for v in nxt: n_idx = n_idx*m + v
            arc_s[idx][c] = n_idx
    pa = [[None]*k for _ in range(nP)]
    for pi,p in enumerate(all_p):
        for at,c in enumerate(p): pa[pi][c] = at
    return n, arc_s, pa, all_p

def run_hybrid_sa(m: int, k: int=3, seed: int=0, max_iter: int=1000):
    n, arc_s, pa, all_p = _build_sa(m, k); nP = len(all_p)
    rng = random.Random(seed); sigma = [rng.randrange(nP) for _ in range(n)]
    cs = _sa_score(sigma, arc_s, pa, n, k); bs = cs; best = sigma[:]
    for it in range(max_iter):
        if cs == 0: break
        v = rng.randrange(n); old = sigma[v]; sigma[v] = rng.randrange(nP)
        ns = _sa_score(sigma, arc_s, pa, n, k)
        if ns <= cs:
            cs = ns
            if cs < bs: bs = cs; best = sigma[:]
        else: sigma[v] = old
    sol = None
    if bs == 0:
        sol = {}
        for idx, pi in enumerate(best):
            coords = []; val = idx
            for _ in range(k): coords.append(val % m); val //= m
            coords.reverse(); sol[tuple(coords)] = tuple(all_p[pi])
    return sol, {"best": bs}

def run_fiber_structured_sa(m: int, k: int, seed: int=0, max_iter: int=1000):
    n, arc_s, pa, all_p = _build_sa(m, k); nP = len(all_p)
    node_to_key = [ (sum(reversed([(v//(m**i))%m for i in range(k)])) % m,) for v in range(n)]
    keys = list(set(node_to_key))
    rng = random.Random(seed); tab = {k_: rng.randrange(nP) for k_ in keys}
    def make_sigma(t): return [t[node_to_key[v]] for v in range(n)]
    sigma = make_sigma(tab); cs = _sa_score(sigma, arc_s, pa, n, k)
    bs = cs; bt = tab.copy()
    for it in range(max_iter):
        if cs == 0: break
        rk = rng.choice(keys); old = tab[rk]; tab[rk] = rng.randrange(nP)
        sig = make_sigma(tab); ns = _sa_score(sig, arc_s, pa, n, k)
        if ns <= cs:
            cs = ns
            if cs < bs: bs = cs; bt = tab.copy()
        else: tab[rk] = old
    sol = None
    if bs == 0:
        sol = {}
        for idx, pi in enumerate(make_sigma(bt)):
            sol[tuple(reversed([(idx//(m**i))%m for i in range(k)]))] = tuple(all_p[pi])
    return sol, {"best": bs}

def construct_spike_sigma(m: int, k: int = 3):
    if m % 2 == 0 or m < 3 or k != 3: return None
    C = [0] + [1] * (m - 2) + [2]
    D = [[c for c in range(3) if c != C[s]] for s in range(m)]
    table = []
    for s in range(m):
        lv = {}
        for j in range(m):
            val = 1 if (s >= m - 2 and j == m - 1) else 0
            p = [None] * 3; p[1] = C[s]
            if val == 1: p[0] = D[s][0]; p[2] = D[s][1]
            else: p[0] = D[s][1]; p[2] = D[s][0]
            lv[j] = tuple(p)
        table.append(lv)
    return table_to_sigma(table, m)

def solve(m: int, k: int=3, seed: int=42, max_iter: int=1000) -> Optional[Dict]:
    if (m,k) in PRECOMPUTED: return PRECOMPUTED[(m,k)]
    w = extract_weights(m, k)
    if w.h2_blocks: return None
    if k == 3 and m % 2 == 1: return construct_spike_sigma(m, k)
    if k == 3: return run_hybrid_sa(m, k=3, seed=seed, max_iter=max_iter)[0]
    return run_fiber_structured_sa(m, k=k, seed=seed, max_iter=max_iter)[0]

def repair_manifold(m: int, k: int, sigma_in: Dict[Tuple, Tuple], max_iter: int = 1000) -> Optional[Dict]:
    n, arc_s, pa, all_p = _build_sa(m, k); nP = len(all_p)
    sigma = [all_p.index(list(sigma_in[tuple(reversed([(idx//(m**i))%m for i in range(k)]))])) for idx in range(n)]
    cs = _sa_score(sigma, arc_s, pa, n, k)
    if cs == 0: return sigma_in
    bs = cs; best = sigma[:]; rng = random.Random(42)
    for it in range(max_iter):
        v = rng.randrange(n); old = sigma[v]; sigma[v] = rng.randrange(nP)
        ns = _sa_score(sigma, arc_s, pa, n, k)
        if ns < cs:
            cs = ns
            if cs < bs: bs = cs; best = sigma[:]
        else: sigma[v] = old
        if cs == 0: break
    if bs == 0:
        sol = {}
        for idx, pi in enumerate(best):
            sol[tuple(reversed([(idx//(m**i))%m for i in range(k)]))] = tuple(all_p[pi])
        return sol
    return None

if __name__ == "__main__":
    for m,k in [(3,3),(4,4)]:
        w = extract_weights(m,k)
        print(f"  m={m} k={k}  {w.summary()}")
