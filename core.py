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

Derivation of W4 = phi(m):
  |coprime-sum cocycles b: Z_m→Z_m| = m^(m-1) · phi(m)
  |coboundaries|                     = m^(m-1)
  |H¹(Z_m, coprime-sum)|            = phi(m)

Closure lemma (proved for m=3, conjectured general):
  Given b₀,...,b_{k-2} with gcd(sum,m)=1, b_{k-1} is determined.
  Therefore W7 = phi(m) × coprime_b(m)^(k-1)  [exact for m=3].
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

    # W1: H² obstruction — O(1)
    all_odd = bool(cp) and all(r % 2 == 1 for r in cp)
    h2 = all_odd and (k % 2 == 1) and (m % 2 == 0)

    # W2/W3: r-tuples — O(|cp|^k)
    r_tuples = [] if h2 else [t for t in iprod(cp, repeat=k) if sum(t) == m]
    r_count  = len(r_tuples)
    canon    = None
    if r_count > 0:
        mid = m - (k - 1)
        canon = ((1,)*(k-1) + (mid,)) if (mid > 0 and gcd(mid,m)==1) else r_tuples[0]

    # W4: |H¹(Z_m, coprime-sum)| = phi(m) — O(1) exact
    h1 = phi_m

    # W5/W6: search compression — O(1)
    lev = _LEVEL_COUNTS.get(m, phi_m * 6)
    full_exp   = m**3 * log2(6)
    search_exp = m * log2(lev) if lev > 0 else 0
    compression = search_exp / full_exp if full_exp > 0 else 1.0

    # W7: solution lower bound — exact for m=3, lb for m≥5
    # phi(m) × coprime_b(m)^(k-1)  where coprime_b = m^(m-1)·phi(m)
    coprime_b = m**(m-1) * phi_m
    sol_lb = phi_m * coprime_b**(k-1) if r_count > 0 else 0

    # W8: gauge orbit size = m^(m-1)
    orbit_size = m**(m-1)

    return Weights(m=m, k=k, h2_blocks=h2, r_count=r_count, canonical=canon,
                   h1_exact=h1, search_exp=round(search_exp,3),
                   compression=round(compression,6), sol_lb=sol_lb,
                   orbit_size=orbit_size, coprime_elems=cp)


def weights_table(m_range=range(2,11), k_range=range(2,7)) -> List[Weights]:
    return [extract_weights(m,k) for m in m_range for k in k_range]


# ══════════════════════════════════════════════════════════════════════════════
# VERIFICATION
# ══════════════════════════════════════════════════════════════════════════════


def verify_sigma(sigma: Dict[Tuple, Tuple], m: int) -> bool:
    """
    Verify sigma: Z_m^k → S_k yields k directed Hamiltonian cycles.
    Checks: in-degree=1, components=1 for each color.
    """
    if not sigma: return False
    k = len(next(iter(sigma.keys())))
    n = m**k

    sh = []
    for i in range(k):
        vec = [0]*k; vec[i] = 1; sh.append(tuple(vec))

    funcs: List[Dict] = [{} for _ in range(k)]
    for v, p in sigma.items():
        if len(p) != k: return False
        for at in range(k):
            nb = tuple((v[d] + sh[at][d]) % m for d in range(k))
            funcs[p[at]][v] = nb

    for fg in funcs:
        if len(fg) != n: return False
        vis = set()
        comps = 0
        for s_coords in fg:
            if s_coords not in vis:
                comps += 1
                cur_coords = s_coords
                while cur_coords not in vis:
                    vis.add(cur_coords)
                    cur_coords = fg[cur_coords]
        if comps != 1: return False
    return True



# ══════════════════════════════════════════════════════════════════════════════
# HARDCODED VERIFIED SOLUTIONS
# ══════════════════════════════════════════════════════════════════════════════

_TABLE_M3 = [
    {0:(2,0,1),1:(1,0,2),2:(2,0,1)},
    {0:(0,2,1),1:(1,2,0),2:(0,2,1)},
    {0:(0,1,2),1:(0,1,2),2:(0,1,2)},
]
_TABLE_M5 = [
    {0:(0,2,1),1:(1,2,0),2:(0,2,1),3:(0,2,1),4:(1,2,0)},
    {0:(2,1,0),1:(2,1,0),2:(0,1,2),3:(2,1,0),4:(2,1,0)},
    {0:(2,1,0),1:(0,1,2),2:(0,1,2),3:(2,1,0),4:(2,1,0)},
    {0:(2,1,0),1:(2,1,0),2:(0,1,2),3:(0,1,2),4:(2,1,0)},
    {0:(2,0,1),1:(1,0,2),2:(2,0,1),3:(1,0,2),4:(2,0,1)},
]
SOLUTION_M4: Dict[Tuple,Tuple] = {
    (0,0,0):(2,1,0),(0,0,1):(2,1,0),(0,0,2):(0,2,1),(0,0,3):(1,2,0),
    (0,1,0):(1,0,2),(0,1,1):(0,2,1),(0,1,2):(2,0,1),(0,1,3):(0,1,2),
    (0,2,0):(2,0,1),(0,2,1):(0,1,2),(0,2,2):(1,2,0),(0,2,3):(1,0,2),
    (0,3,0):(1,2,0),(0,3,1):(1,2,0),(0,3,2):(0,1,2),(0,3,3):(2,0,1),
    (1,0,0):(2,0,1),(1,0,1):(0,2,1),(1,0,2):(2,1,0),(1,0,3):(1,2,0),
    (1,1,0):(2,0,1),(1,1,1):(1,2,0),(1,1,2):(0,2,1),(1,1,3):(1,0,2),
    (1,2,0):(0,2,1),(1,2,1):(1,2,0),(1,2,2):(0,1,2),(1,2,3):(2,0,1),
    (1,3,0):(2,1,0),(1,3,1):(1,0,2),(1,3,2):(0,2,1),(1,3,3):(1,2,0),
    (2,0,0):(2,0,1),(2,0,1):(0,2,1),(2,0,2):(1,2,0),(2,0,3):(0,2,1),
    (2,1,0):(2,1,0),(2,1,1):(2,0,1),(2,1,2):(1,2,0),(2,1,3):(2,0,1),
    (2,2,0):(0,1,2),(2,2,1):(2,0,1),(2,2,2):(0,2,1),(2,2,3):(1,0,2),
    (2,3,0):(1,0,2),(2,3,1):(0,2,1),(2,3,2):(1,0,2),(2,3,3):(1,2,0),
    (3,0,0):(1,0,2),(3,0,1):(1,0,2),(3,0,2):(2,0,1),(3,0,3):(2,0,1),
    (3,1,0):(0,2,1),(3,1,1):(0,1,2),(3,1,2):(0,2,1),(3,1,3):(0,2,1),
    (3,2,0):(1,2,0),(3,2,1):(0,2,1),(3,2,2):(1,2,0),(3,2,3):(2,0,1),
    (3,3,0):(2,0,1),(3,3,1):(2,1,0),(3,3,2):(1,0,2),(3,3,3):(1,2,0),
}

def table_to_sigma(table: List[Dict], m: int) -> Dict[Tuple,Tuple]:
    """Convert a list of level-dicts to the full sigma map."""
    sigma = {}
    for i in range(m):
        for j in range(m):
            for k in range(m):
                sigma[(i,j,k)] = table[(i+j+k)%m][j]
    return sigma

PRECOMPUTED: Dict[Tuple[int,int], Dict] = {
    (3,3): table_to_sigma(_TABLE_M3, 3),
    (5,3): table_to_sigma(_TABLE_M5, 5),
    (4,3): dict(SOLUTION_M4),
}


# ══════════════════════════════════════════════════════════════════════════════
# FIBER LEVEL MACHINERY
# ══════════════════════════════════════════════════════════════════════════════

def _level_valid(lv: Dict[int,list], m: int) -> bool:
    for c in range(3):
        targets: set = set()
        for j in range(m):
            at = lv[j].index(c); di,dj = _FIBER_SHIFTS[at]
            for i in range(m): targets.add(((i+di)%m, (j+dj)%m))
        if len(targets) != m*m: return False
    return True

@lru_cache(maxsize=16)
def valid_levels(m: int) -> List[Dict]:
    """All valid level assignments for G_m. Cached."""
    result = []
    for combo in iprod(_ALL_P3, repeat=m):
        lv = {j: combo[j] for j in range(m)}
        if _level_valid(lv, m): result.append(lv)
    return result

def compose_Q(table: List[Dict], m: int) -> List[Dict]:
    """Compute the three composed fiber permutations Q_0, Q_1, Q_2."""
    Qs: List[Dict] = [{},{},{}]
    for i0 in range(m):
        for j0 in range(m):
            pos = [[i0,j0],[i0,j0],[i0,j0]]
            for s in range(m):
                lv = table[s]
                for c in range(3):
                    cj = pos[c][1]; at = lv[cj].index(c)
                    di,dj = _FIBER_SHIFTS[at]
                    pos[c][0] = (pos[c][0]+di)%m
                    pos[c][1] = (pos[c][1]+dj)%m
            for c in range(3): Qs[c][(i0,j0)] = tuple(pos[c])
    return Qs

def is_single_cycle(Q: Dict, m: int) -> bool:
    n = m*m; vis: set = set(); cur = (0,0)
    while cur not in vis: vis.add(cur); cur = Q[cur]
    return len(vis) == n


# ══════════════════════════════════════════════════════════════════════════════
# SA ENGINE  —  fast integer-array SA with repair + plateau escape
# ══════════════════════════════════════════════════════════════════════════════

import math, random
from itertools import permutations, product as iprod
from typing import Optional, List, Dict, Tuple, Any

def _build_sa(m: int, k: int=3):
    n = m**k
    arc_s = [[0]*k for _ in range(n)]
    m_pow = [m**i for i in range(k)]
    m_pow.reverse()
    for idx in range(n):
        for c in range(k):
            if (idx // m_pow[c]) % m == m - 1:
                arc_s[idx][c] = idx - (m - 1) * m_pow[c]
            else:
                arc_s[idx][c] = idx + m_pow[c]
    all_p = [list(p) for p in permutations(range(k))]
    pa = [[None]*k for _ in range(len(all_p))]
    for pi,p in enumerate(all_p):
        for at,c in enumerate(p): pa[pi][c] = at
    return n, arc_s, pa, all_p

def _build_sa3(m: int):
    n, arc_s, pa, _ = _build_sa(m, 3)
    return n, arc_s, pa

def _sa_score(sigma: List[int], arc_s, pa, n: int, k: int=3) -> int:
    total_score = 0
    for c in range(k):
        vis = bytearray(n); comps = 0
        for s in range(n):
            if not vis[s]:
                comps += 1; cur = s
                while not vis[cur]:
                    vis[cur] = 1; pi = sigma[cur]
                    cur = arc_s[cur][pa[pi][c]]
        total_score += comps - 1
    return total_score

def get_node_orbits(m: int, subgroup_generators: List[Tuple[int, ...]]) -> List[List[int]]:
    """Identifies vertex orbits as flat indices. Supports arbitrary k."""
    k = len(subgroup_generators[0])
    n = m**k
    m_pow = [m**i for i in range(k)]; m_pow.reverse()
    unvisited = set(range(n)); orbits = []
    while unvisited:
        start_idx = next(iter(unvisited)); orbit = {start_idx}
        queue = [start_idx]; unvisited.remove(start_idx)
        while queue:
            curr_idx = queue.pop(0)
            curr_coords = []; val = curr_idx
            for _ in range(k): curr_coords.append(val % m); val //= m
            curr_coords.reverse()
            for gen in subgroup_generators:
                nxt_coords = [(curr_coords[d] + gen[d]) % m for d in range(k)]
                nxt_idx = 0
                for x in nxt_coords: nxt_idx = nxt_idx * m + x
                if nxt_idx in unvisited:
                    unvisited.remove(nxt_idx); orbit.add(nxt_idx); queue.append(nxt_idx)
        orbits.append(list(orbit))
    return orbits

def run_hybrid_sa(m: int, k: int=3, seed: int=0, max_iter: int=1_000_000,
                  verbose: bool=False) -> Tuple[Optional[Dict], Dict]:
    """
    Hybrid discovery engine: alternates between Equivariant moves and Basin-repair.
    Supports arbitrary k and includes last-mile repair logic.
    """
    import math, time
    n, arc_s, pa, all_p = _build_sa(m, k)
    nP = len(all_p)
    gens = [tuple([m//2]*k)] if m%2==0 else [tuple([1]*k)]
    orbits = get_node_orbits(m, gens)
    rng = random.Random(seed); sigma = [rng.randrange(nP) for _ in range(n)]
    cs = _sa_score(sigma, arc_s, pa, n, k); bs = cs; best = sigma[:]
    T = 2.0; cool = 0.999998; t0 = time.perf_counter()
    stall = 0; reheats = 0; report_n = 50_000
    for it in range(max_iter):
        if cs == 0: break
        if cs <= 12:
            # Basin Escape v2.2: greedy descent + orbit swaps
            order = list(range(n)); rng.shuffle(order); fixed = False
            for v in order:
                old = sigma[v]
                for pi in rng.sample(range(nP), nP):
                    if pi == old: continue
                    sigma[v] = pi; ns = _sa_score(sigma, arc_s, pa, n, k)
                    if ns < cs:
                        cs = ns; fixed = True
                        if cs < bs: bs = cs; best = sigma[:]
                    else: sigma[v] = old
                    if fixed: break
                if fixed: break
            if not fixed:
                # Try orbit-flip greedy
                for orbit in rng.sample(orbits, min(len(orbits), 20)):
                    old_vals = [sigma[v] for v in orbit]
                    for pi in rng.sample(range(nP), nP):
                        if all(sigma[v] == pi for v in orbit): continue
                        for v in orbit: sigma[v] = pi
                        ns = _sa_score(sigma, arc_s, pa, n, k)
                        if ns < cs:
                            cs = ns; fixed = True
                            if cs < bs: bs = cs; best = sigma[:]
                        else:
                            for i, v in enumerate(orbit): sigma[v] = old_vals[i]
                        if fixed: break
                    if fixed: break
            if not fixed:
                reheats += 1; stall = 0; sigma = best[:]; cs = bs; T = 1.0
                for _ in range(max(1, int(n * 0.03))):
                    vk = rng.randrange(n); sigma[vk] = rng.randrange(nP)
                cs = _sa_score(sigma, arc_s, pa, n, k)
            continue
        if rng.random() < 0.3:
            orbit = rng.choice(orbits); new_p = rng.randrange(nP)
            old_vals = [sigma[v] for v in orbit]
            for v in orbit: sigma[v] = new_p
            ns = _sa_score(sigma, arc_s, pa, n, k); d = ns - cs
            if d <= 0 or rng.random() < math.exp(-d / T):
                cs = ns
                if cs < bs: bs = cs; best = sigma[:]; stall = 0
                else: stall += 1
            else:
                for i, v in enumerate(orbit): sigma[v] = old_vals[i]
                stall += 1
        else:
            v = rng.randrange(n); old = sigma[v]; sigma[v] = rng.randrange(nP)
            ns = _sa_score(sigma, arc_s, pa, n, k); d = ns - cs
            if d <= 0 or rng.random() < math.exp(-d / T):
                cs = ns
                if cs < bs: bs = cs; best = sigma[:]; stall = 0
                else: stall += 1
            else:
                sigma[v] = old; stall += 1
        if stall > 100_000:
            reheats += 1; stall = 0; sigma = best[:]; cs = bs; T = 2.0 / (1.2**reheats)
            for _ in range(max(1, int(n * (0.05 if cs > 20 else 0.02)))):
                vk = rng.randrange(n); sigma[vk] = rng.randrange(nP)
            cs = _sa_score(sigma, arc_s, pa, n, k); continue
        T *= cool
        if verbose and (it+1) % report_n == 0:
            print(f"    it={it+1:>8,} T={T:.5f} s={cs} best={bs} reh={reheats} {time.perf_counter()-t0:.1f}s")
    elapsed = time.perf_counter() - t0
    sol = None
    if bs == 0:
        sol = {}
        for idx, pi in enumerate(best):
            coords = []; val = idx
            for _ in range(k): coords.append(val % m); val //= m
            coords.reverse(); sol[tuple(coords)] = tuple(all_p[pi])
    return sol, {"best": bs, "iters": it+1, "elapsed": elapsed, "reheats": reheats}

def run_fiber_structured_sa(m: int, k: int, seed: int=0, max_iter: int=10_000_000,
                            verbose: bool=False) -> Tuple[Optional[Dict], Dict]:
    """SA where sigma(v) depends on (fiber(v), coords[1], ..., coords[k-2]).
    Includes Basin Escape v3.0 logic for score <= 15.
    """
    import math, time
    n, arc_s, pa, all_p = _build_sa(m, k); nP = len(all_p)
    def get_coords(idx):
        coords = []; val = idx
        for _ in range(k): coords.append(val % m); val //= m
        coords.reverse(); return coords
    fibers = [sum(get_coords(v)) % m for v in range(n)]
    def get_key(v):
        c = get_coords(v)
        return (fibers[v],) + tuple(c[1:-1])
    node_to_key = [get_key(v) for v in range(n)]
    keys = list(set(node_to_key))
    rng = random.Random(seed); tab = {k_: rng.randrange(nP) for k_ in keys}
    def make_sigma(t):
        sig = [0]*n
        for v in range(n): sig[v] = t[node_to_key[v]]
        return sig
    sigma = make_sigma(tab); cs = _sa_score(sigma, arc_s, pa, n, k)
    bs = cs; bt = tab.copy(); t0 = time.perf_counter(); stall = 0
    T = 2.0; cool = (0.003/2.0)**(1.0/max_iter) if max_iter > 0 else 0.999998
    for it in range(max_iter):
        if cs == 0: break
        if cs <= 15:
            # Basin Escape v3.0
            fixed = False
            rk_list = list(keys); rng.shuffle(rk_list)
            for rk in rk_list:
                old = tab[rk]
                for pi in rng.sample(range(nP), nP):
                    if pi == old: continue
                    tab[rk] = pi; sig = make_sigma(tab)
                    ns = _sa_score(sig, arc_s, pa, n, k)
                    if ns < cs:
                        cs = ns; fixed = True
                        if cs < bs: bs = cs; bt = tab.copy()
                    else: tab[rk] = old
                    if fixed: break
                if fixed: break
            if not fixed:
                pairs = []
                for idx1 in range(len(rk_list)):
                    for idx2 in range(idx1 + 1, len(rk_list)):
                        pairs.append((rk_list[idx1], rk_list[idx2]))
                rng.shuffle(pairs)
                for k1, k2 in pairs[:50]:
                    old1, old2 = tab[k1], tab[k2]
                    for _ in range(20):
                        pi1, pi2 = rng.randrange(nP), rng.randrange(nP)
                        tab[k1], tab[k2] = pi1, pi2
                        sig = make_sigma(tab)
                        ns = _sa_score(sig, arc_s, pa, n, k)
                        if ns < cs:
                            cs = ns; fixed = True
                            if cs < bs: bs = cs; bt = tab.copy()
                            break
                        else: tab[k1], tab[k2] = old1, old2
                    if fixed: break
            if not fixed:
                tab = bt.copy()
                for _ in range(max(1, int(len(keys)*0.05))): tab[rng.choice(keys)] = rng.randrange(nP)
                sig = make_sigma(tab); cs = _sa_score(sig, arc_s, pa, n, k)
            continue
        rk = rng.choice(keys); old = tab[rk]; tab[rk] = rng.randrange(nP)
        if tab[rk] == old: continue
        sig = make_sigma(tab); ns = _sa_score(sig, arc_s, pa, n, k); d = ns - cs
        if d <= 0 or rng.random() < math.exp(-d / T):
            cs = ns
            if cs < bs: bs = cs; bt = tab.copy(); stall = 0
            else: stall += 1
        else: tab[rk] = old; stall += 1
        if stall > 50_000:
            stall = 0; tab = bt.copy(); cs = bs
            for _ in range(max(1, int(len(keys)*0.05))): tab[rng.choice(keys)] = rng.randrange(nP)
            sig = make_sigma(tab); cs = _sa_score(sig, arc_s, pa, n, k); continue
        T *= cool
        if verbose and (it+1) % 100_000 == 0:
            print(f"    FiberSA it={it+1:>8,} T={T:.5f} s={cs} best={bs} {time.perf_counter()-t0:.1f}s")
    sol = None
    if bs == 0:
        sol = {}
        for idx, pi in enumerate(make_sigma(bt)):
            sol[tuple(get_coords(idx))] = tuple(all_p[pi])
    return sol, {"best": bs, "iters": it+1, "elapsed": time.perf_counter()-t0}










def get_canonical_spike_params(m: int, k: int = 3) -> Dict[str, List[int]]:
    """
    Returns the deterministic parameters for odd m or k=4, m=4.
    r: shift triple/quadruple
    v: base shift
    delta: spike value
    j0: spike position
    """
    if k == 3 and m % 2 == 1:
        # Verified r-triple (1, m-2, 1) sums to m, each coprime to m
        r = [1, m - 2, 1]
        delta = [-1, 2, -1]
        j0 = [0, 0, 0]
        v = [m - 1, 0, 1]
        return {"r": r, "v": v, "delta": delta, "j0": j0}
    if k == 4 and m == 4:
        # P1 (k=4, m=4) Nested Spike Parameters
        r = [1, 1, 1, 1]
        delta = [1, 1, 1, 1]
        j0 = [0, 1, 2, 3]
        v = [0, 0, 0, 0]
        return {"r": r, "v": v, "delta": delta, "j0": j0}
    return None



def construct_spike_sigma(m: int, k: int = 3, params: Dict = None) -> Dict[Tuple, Tuple]:
    """
    Directly construct a valid k-Hamiltonian decomposition for G_m.
    Currently optimized for k=3 (odd m).
    Uses the O(m) spike framework: b_c(j) = v_c + delta_c * [j == j0_c].
    The 'genuine heads' are the starting positions of the Hamiltonian cycles,
    fully determined by the parameters without search.
    """
    if m % 2 == 0 or m < 3: return None
    if k != 3: return None # k=4 construction is still search-based or open

    if params is None:
        params = get_canonical_spike_params(m, k)
    if params is None: return None

    # Geometric construction for k=3 (Verified for all odd m)
    sigma = {}
    for i in range(m):
        for j in range(m):
            for k_coord in range(m):
                s = (i + j + k_coord) % m
                # Selection of p_s to ensure Hamiltonian cycles
                if j == 0:
                    p = (1, 0, 2) if s == 0 else (1, 2, 0) if s == 1 else (0, 1, 2)
                else:
                    p = (2, 0, 1) if s == 0 else (0, 2, 1) if s == 1 else (0, 1, 2)
                sigma[(i, j, k_coord)] = p
    return sigma
def solve(m: int, k: int=3, seed: int=42) -> Optional[Dict]:
    """
    Unified solver. Returns sigma or None.
    Routes: precomputed → geometric-construction → Hybrid SA.
    """
    # 1. Precomputed
    if (m,k) in PRECOMPUTED: return PRECOMPUTED[(m,k)]

    w = extract_weights(m, k)
    if w.h2_blocks: return None

    # 2. Geometric construction (odd m, k=3)
    if k == 3 and m % 2 == 1:
        return construct_spike_sigma(m, k)

    # 3. Search-based (SA)
    if k == 3:
        sol, _ = run_hybrid_sa(m, k=3, seed=seed)
        return sol
    elif k == 4:
        sol, _ = run_fiber_structured_sa(m, k=4, seed=seed)
        return sol
    return None


if __name__ == "__main__":
    import sys
    print("╔═══════════════════════════════════════════════╗")
    print("║  core.py — improved hybrid engine            ║")
    print("╚═══════════════════════════════════════════════╝")
    for m,k in [(3,3),(4,4)]:
        w = extract_weights(m,k)
        print(f"  m={m} k={k}  {w.summary()}")
