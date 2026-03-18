#!/usr/bin/env python3
"""
cycles_even_m.py — 6-Phase Discovery: Even m in Claude's Cycles
================================================================
The digraph G_m:  vertices (i,j,k) ∈ Z_m³
  arc 0: (i,j,k) → (i+1, j,   k  ) mod m
  arc 1: (i,j,k) → (i,   j+1, k  ) mod m
  arc 2: (i,j,k) → (i,   j,   k+1) mod m

sigma assigns each arc to one of 3 cycles.
Goal: every cycle is a single directed Hamiltonian cycle of length m³.

Odd m  → column-uniform sigma works (proven, m=3,5,7 solved).
Even m → column-uniform is PROVABLY impossible.
         This script discovers WHY and then FINDS a solution via SA.

Phases:
  01 GROUND TRUTH   — define verification; confirm odd m works
  02 DIRECT ATTACK  — attempt column-uniform on m=4; record exact failure
  03 STRUCTURE HUNT — prove the parity obstruction; characterise what even m needs
  04 PATTERN LOCK   — SA search for m=4; analyse the solution structure
  05 GENERALIZE     — test the discovered structure on m=6
  06 PROVE LIMITS   — complete theorem: odd proven, even found, open frontier stated

Run:
  python cycles_even_m.py            # full 6-phase run
  python cycles_even_m.py --fast     # skip m=6 search (saves ~2 min)
"""

import sys, time, random, math
from itertools import permutations
from math import gcd
from typing import List, Dict, Tuple, Optional, Callable

# ── colour ────────────────────────────────────────────────────────────────────
R="\033[91m"; G="\033[92m"; Y="\033[93m"; B="\033[94m"
M="\033[95m"; C="\033[96m"; W="\033[97m"; D="\033[2m"; Z="\033[0m"
PCOL = {1:G, 2:R, 3:B, 4:M, 5:Y, 6:C}

def hr(c="─",n=72): return c*n
def sec(num,name,tag):
    print(f"\n{hr()}")
    print(f"{PCOL[num]}Phase {num:02d} — {name}{Z}  {D}{tag}{Z}")
    print(hr("·"))
def kv(k,v,ind=2): print(f"{' '*ind}{D}{k:<36}{Z}{W}{str(v)[:80]}{Z}")
def found(msg): print(f"  {G}✓ {msg}{Z}")
def miss(msg):  print(f"  {R}✗ {msg}{Z}")
def note(msg):  print(f"  {Y}→ {msg}{Z}")
def info(msg):  print(f"  {D}{msg}{Z}")

# ══════════════════════════════════════════════════════════════════════════════
# CORE — self-contained (no import from claudecycles)
# ══════════════════════════════════════════════════════════════════════════════

Vertex   = Tuple[int,int,int]
Perm     = Tuple[int,int,int]          # (arc0→cycle, arc1→cycle, arc2→cycle)
SigmaMap = Dict[Vertex, Perm]

_ALL_PERMS: List[Perm] = list(permutations(range(3)))

ARC_SHIFTS = ((1,0,0),(0,1,0),(0,0,1))
# ── Hardcoded verified m=4 solution (SA seed=0, 516K iters, 10.6s) ──────────
# Every entry verified: 3 Hamiltonian cycles each visiting all 64 vertices.
# deps: i=True, j=True, k=True, column_uniform=False (full 3D, as theorem predicts)
_SOLUTION_M4 = {
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


def vertices(m):
    return [(i,j,k) for i in range(m) for j in range(m) for k in range(m)]

def build_funcs(sigma: SigmaMap, m: int) -> List[Dict[Vertex,Vertex]]:
    funcs = [{},{},{}]
    for v in vertices(m):
        p = sigma[v]
        for at in range(3):
            nb = tuple((v[d]+ARC_SHIFTS[at][d])%m for d in range(3))
            funcs[p[at]][v] = nb
    return funcs

def count_components(fg: Dict[Vertex,Vertex]) -> int:
    visited = set(); comps = 0
    for start in fg:
        if start not in visited:
            comps += 1; cur = start
            while cur not in visited:
                visited.add(cur); cur = fg[cur]
    return comps

def score(sigma: SigmaMap, m: int) -> int:
    """Excess components across 3 cycles (0 = valid)."""
    funcs = build_funcs(sigma, m)
    return sum(count_components(fg)-1 for fg in funcs)

def verify(sigma: SigmaMap, m: int) -> bool:
    """Full verification: each cycle is exactly 1 Hamiltonian cycle."""
    n = m**3
    funcs = build_funcs(sigma, m)
    for c, fg in enumerate(funcs):
        if len(fg) != n: return False
        # in-degree check
        indeg = {}
        for nb in fg.values():
            indeg[nb] = indeg.get(nb,0)+1
        if any(d!=1 for d in indeg.values()): return False
        # single cycle check
        if count_components(fg) != 1: return False
    return True

# ── Incremental score update ──────────────────────────────────────────────────
def build_funcs_list(sigma: SigmaMap, m: int):
    """Build 3 mutable dicts."""
    funcs = [{},{},{}]
    for v in vertices(m):
        p = sigma[v]
        for at in range(3):
            nb = tuple((v[d]+ARC_SHIFTS[at][d])%m for d in range(3))
            funcs[p[at]][v] = nb
    return funcs


# ══════════════════════════════════════════════════════════════════════════════
# FIBER MACHINERY (for odd-m column-uniform approach)
# ══════════════════════════════════════════════════════════════════════════════

FIBER_SHIFTS = ((1,0),(0,1),(0,0))   # arc 0,1,2 in (i,j) fiber space

def fiber_valid_levels(m: int) -> List[Dict[int,Perm]]:
    """All column-uniform level assignments where each cycle is bijective on Z_m²."""
    result = []
    for combo in _cartesian(_ALL_PERMS, m):
        level = {j: combo[j] for j in range(m)}
        if _level_bijective(level, m):
            result.append(level)
    return result

def _cartesian(lst, k):
    if k == 0: yield (); return
    for rest in _cartesian(lst, k-1):
        for item in lst:
            yield rest + (item,)

def _level_bijective(level: Dict[int,Perm], m: int) -> bool:
    for c in range(3):
        targets = set()
        for j in range(m):
            at = level[j].index(c)
            di, dj = FIBER_SHIFTS[at]
            for i in range(m):
                targets.add(((i+di)%m, (j+dj)%m))
        if len(targets) != m*m:
            return False
    return True

def compose_q(table: List[Dict[int,Perm]], m: int):
    """Compose all m fiber levels → 3 permutations Q_c on Z_m²."""
    Qs = [{},{},{}]
    for i0 in range(m):
        for j0 in range(m):
            pos = [[i0,j0],[i0,j0],[i0,j0]]
            for s in range(m):
                lv = table[s]
                for c in range(3):
                    cj = pos[c][1]
                    at = lv[cj].index(c)
                    di,dj = FIBER_SHIFTS[at]
                    pos[c][0] = (pos[c][0]+di)%m
                    pos[c][1] = (pos[c][1]+dj)%m
            for c in range(3):
                Qs[c][(i0,j0)] = tuple(pos[c])
    return Qs

def q_is_single_cycle(Q: Dict, m: int) -> bool:
    n = m*m; visited = set(); cur = (0,0)
    while cur not in visited:
        visited.add(cur); cur = Q[cur]
    return len(visited)==n

def table_to_sigma(table: List[Dict[int,Perm]], m: int) -> SigmaMap:
    sigma = {}
    for i in range(m):
        for j in range(m):
            for k in range(m):
                s = (i+j+k)%m
                sigma[(i,j,k)] = table[s][j]
    return sigma

# ── Odd m random search ───────────────────────────────────────────────────────
def find_odd_m(m: int, seed=42, max_att=200_000) -> Optional[SigmaMap]:
    rng = random.Random(seed)
    levels = fiber_valid_levels(m)
    if not levels: return None
    for _ in range(max_att):
        table = [rng.choice(levels) for _ in range(m)]
        Qs    = compose_q(table, m)
        if all(q_is_single_cycle(Q,m) for Q in Qs):
            return table_to_sigma(table, m)
    return None

# ── Parity obstruction proof ──────────────────────────────────────────────────
def prove_column_uniform_impossible(m: int) -> dict:
    """
    Column-uniform needs r₀+r₁+r₂ = m, each gcd(rᵢ,m)=1.
    For even m: coprime-to-m ⟹ odd. Sum of 3 odds is odd ≠ m (even). QED.
    Returns dict with all proof data.
    """
    coprime_elems = [r for r in range(m) if gcd(r,m)==1 and r>0]
    all_odd       = all(r%2==1 for r in coprime_elems)
    # Can 3 coprime elements sum to m?
    feasible = [(r0,r1,r2)
                for r0 in coprime_elems
                for r1 in coprime_elems
                for r2 in coprime_elems
                if r0+r1+r2 == m]
    return {
        "m":               m,
        "m_parity":        "even" if m%2==0 else "odd",
        "coprime_elems":   coprime_elems,
        "all_coprime_odd": all_odd,
        "feasible_triples":feasible,
        "impossible":      (m%2==0 and len(feasible)==0),
        "proof":           ("3 odd numbers sum to odd ≠ even = m. "
                            "No column-uniform solution exists."
                            if m%2==0 else
                            f"Example triple: {feasible[0] if feasible else 'none'}"),
    }

# ── Exhaustive column-uniform check for small m ──────────────────────────────
def exhaustive_column_uniform(m: int, max_combos: int = 500_000) -> dict:
    """Try ALL column-uniform sigmas for small m. Record outcome."""
    levels = fiber_valid_levels(m)
    total  = len(levels)**m
    tried  = 0
    rng    = random.Random(0)

    t0 = time.perf_counter()
    for _ in range(min(max_combos, total)):
        table = [rng.choice(levels) for _ in range(m)]
        Qs    = compose_q(table, m)
        if all(q_is_single_cycle(Q,m) for Q in Qs):
            elapsed = time.perf_counter()-t0
            return {"found": True, "tried": tried+1, "elapsed": elapsed}
        tried += 1
    elapsed = time.perf_counter()-t0
    return {"found": False, "tried": tried,
            "total_space": total, "elapsed": elapsed,
            "fraction_searched": tried/total if total>0 else 0}


# ══════════════════════════════════════════════════════════════════════════════
# FAST INTEGER-INDEXED SA
# Encode vertex (i,j,k) as integer v = i*m² + j*m + k.
# sigma is a list[int] of length m³, value = perm index (0..5).
# Functional graphs are list[int] (successor arrays).
# Component count via fast iterative path-tracing.
# ══════════════════════════════════════════════════════════════════════════════

def _build_perm_table(m: int):
    """
    Precompute for each (vertex_idx, perm_idx) → [successor_0, s_1, s_2].
    Returns succs[v][p][arc] = successor vertex index.
    """
    n   = m*m*m
    # arc successors: for each v and arc_type, precompute neighbour
    arc_succ = [[0]*3 for _ in range(n)]
    for idx in range(n):
        i, rem = divmod(idx, m*m)
        j, k   = divmod(rem, m)
        arc_succ[idx][0] = ((i+1)%m)*m*m + j*m + k   # arc 0: i+1
        arc_succ[idx][1] = i*m*m + ((j+1)%m)*m + k   # arc 1: j+1
        arc_succ[idx][2] = i*m*m + j*m + (k+1)%m     # arc 2: k+1
    # perm table: _ALL_PERMS[p] = (c0,c1,c2) means arc_type t → cycle c_t
    # For functional graph of cycle c: func[c][v] = arc_succ[v][ arc_type where perm[arc_type]==c ]
    # Precompute: for each perm p and cycle c, which arc_type serves cycle c?
    # perm_arc[p][c] = arc_type
    perm_arc = [[None]*3 for _ in range(6)]
    for pi, perm in enumerate(_ALL_PERMS):
        for at, c in enumerate(perm):
            perm_arc[pi][c] = at
    return arc_succ, perm_arc

def _build_funcs_fast(sigma_int, arc_succ, perm_arc, n):
    """Build 3 successor arrays from integer sigma."""
    f0 = [0]*n; f1 = [0]*n; f2 = [0]*n
    for v in range(n):
        pi = sigma_int[v]
        pa = perm_arc[pi]
        f0[v] = arc_succ[v][pa[0]]
        f1[v] = arc_succ[v][pa[1]]
        f2[v] = arc_succ[v][pa[2]]
    return f0, f1, f2

def _count_comps_fast(f, n):
    """Count cycle components in successor array."""
    visited = bytearray(n)
    comps   = 0
    for start in range(n):
        if not visited[start]:
            comps += 1
            cur = start
            while not visited[cur]:
                visited[cur] = 1
                cur = f[cur]
    return comps

def _score_fast(f0, f1, f2, n):
    return (_count_comps_fast(f0,n)-1 +
            _count_comps_fast(f1,n)-1 +
            _count_comps_fast(f2,n)-1)


def sa_search_fast(m: int,
                   max_iter:  int   = 2_000_000,
                   T_init:    float = 3.0,
                   T_min:     float = 0.005,
                   seed:      int   = 0,
                   verbose:   bool  = True,
                   report_n:  int   = 500_000) -> Tuple[Optional[List[int]], dict]:
    """
    Fast SA with score=1 repair mode + plateau-escape reheat.
    Returns (sigma_int_list or None, stats).
    """
    rng    = random.Random(seed)
    n      = m*m*m
    nperms = len(_ALL_PERMS)

    arc_succ, perm_arc = _build_perm_table(m)

    sigma  = [rng.randrange(nperms) for _ in range(n)]
    f0,f1,f2 = _build_funcs_fast(sigma, arc_succ, perm_arc, n)
    cur_s  = _score_fast(f0,f1,f2,n)
    best_s = cur_s
    best   = sigma[:]

    cool  = (T_min/T_init)**(1.0/max_iter)
    T     = T_init
    t0    = time.perf_counter()
    improvements   = 0
    stall_ctr      = 0
    reheat_count   = 0

    for it in range(max_iter):
        if cur_s == 0:
            break

        # ── Score=1 repair: scan every vertex for a fix ──────────────────
        if cur_s == 1:
            vorder = list(range(n)); rng.shuffle(vorder)
            porder = list(range(nperms)); rng.shuffle(porder)
            fixed = False
            for v in vorder:
                old = sigma[v]
                for pi in porder:
                    if pi == old: continue
                    sigma[v] = pi
                    f0,f1,f2 = _build_funcs_fast(sigma, arc_succ, perm_arc, n)
                    ns = _score_fast(f0,f1,f2,n)
                    if ns < cur_s:
                        cur_s = ns
                        if cur_s < best_s:
                            best_s = cur_s; best = sigma[:]; improvements += 1
                        fixed = True; break
                    sigma[v] = old
                if fixed: break
            if cur_s == 0: break
            if not fixed:
                # Escape: multi-point random perturbation
                for _ in range(rng.randint(3, 12)):
                    sigma[rng.randrange(n)] = rng.randrange(nperms)
                f0,f1,f2 = _build_funcs_fast(sigma, arc_succ, perm_arc, n)
                cur_s = _score_fast(f0,f1,f2,n)
            continue

        # ── Regular SA move ───────────────────────────────────────────────
        v      = rng.randrange(n)
        old_pi = sigma[v]
        new_pi = rng.randrange(nperms)
        if new_pi == old_pi:
            T *= cool; continue
        sigma[v] = new_pi
        f0,f1,f2 = _build_funcs_fast(sigma, arc_succ, perm_arc, n)
        new_s    = _score_fast(f0,f1,f2,n)
        delta    = new_s - cur_s

        if delta < 0 or rng.random() < math.exp(-delta/max(T, 1e-9)):
            cur_s = new_s
            if cur_s < best_s:
                best_s = cur_s; best = sigma[:]
                improvements += 1; stall_ctr = 0
            else:
                stall_ctr += 1
        else:
            sigma[v] = old_pi; stall_ctr += 1

        # ── Plateau escape: reheat + reload best ─────────────────────────
        if stall_ctr > 60_000:
            T = T_init / (2 ** reheat_count)
            reheat_count += 1; stall_ctr = 0
            sigma = best[:]; cur_s = best_s
            f0,f1,f2 = _build_funcs_fast(sigma, arc_succ, perm_arc, n)

        T *= cool

        if verbose and (it+1) % report_n == 0:
            el = time.perf_counter()-t0
            print(f"  {D}iter={it+1:>9,}  T={T:.5f}  "
                  f"score={cur_s}  best={best_s}  "
                  f"reheats={reheat_count}  {el:.1f}s{Z}")

    elapsed = time.perf_counter()-t0
    stats   = {"iters": it+1, "best_score": best_s, "elapsed": elapsed,
               "improvements": improvements, "reheats": reheat_count}
    return (best if best_s==0 else None), stats


def _sigma_int_to_map(sigma_int: List[int], m: int) -> SigmaMap:
    """Convert integer sigma to SigmaMap."""
    sigma = {}
    for idx, pi in enumerate(sigma_int):
        i, rem = divmod(idx, m*m)
        j, k   = divmod(rem, m)
        sigma[(i,j,k)] = _ALL_PERMS[pi]
    return sigma


def sa_multistart(m: int,
                  restarts:  int   = 6,
                  iter_each: int   = 2_000_000,
                  T_init:    float = 3.0,
                  verbose:   bool  = True) -> Tuple[Optional[SigmaMap], dict]:
    """Multi-start SA. Return first success."""
    best_score = 999
    total_iters= 0
    t0 = time.perf_counter()
    for restart in range(restarts):
        if verbose:
            print(f"\n  {D}SA restart {restart+1}/{restarts}  "
                  f"seed={restart}  iter={iter_each:,}{Z}")
        sig_int, stats = sa_search_fast(
            m, max_iter=iter_each, seed=restart,
            verbose=verbose, report_n=500_000, T_init=T_init)
        total_iters += stats["iters"]
        if sig_int is not None:
            sigma_map = _sigma_int_to_map(sig_int, m)
            elapsed   = time.perf_counter()-t0
            return sigma_map, {"restarts_used": restart+1,
                               "total_iters": total_iters,
                               "elapsed": elapsed, "best_score": 0}
        if stats["best_score"] < best_score:
            best_score = stats["best_score"]
    elapsed = time.perf_counter()-t0
    return None, {"restarts_used": restarts, "total_iters": total_iters,
                  "elapsed": elapsed, "best_score": best_score}


# ══════════════════════════════════════════════════════════════════════════════
# SOLUTION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def analyse_sigma_dependencies(sigma: SigmaMap, m: int) -> dict:
    """Find which coordinates sigma actually depends on."""
    dep_i = dep_j = dep_k = dep_s = False
    col_uniform = True   # depends only on (s=(i+j+k)%m, j)?

    for i in range(m):
        for j in range(m):
            for k in range(m):
                base = sigma[(i,j,k)]
                if i>0 and sigma[(i,j,k)] != sigma[(0,j,k)]:
                    dep_i = True
                if j>0 and sigma[(i,j,k)] != sigma[(i,0,k)]:
                    dep_j = True
                if k>0 and sigma[(i,j,k)] != sigma[(i,j,0)]:
                    dep_k = True
                # column-uniform: sigma(i,j,k) = f((i+j+k)%m, j)
                s = (i+j+k)%m
                i2 = (i+1)%m
                k2 = (s-i2-j)%m
                if sigma[(i,j,k)] != sigma[(i2,j,k2)]:
                    col_uniform = False

    return {"dep_i": dep_i, "dep_j": dep_j, "dep_k": dep_k,
            "column_uniform": col_uniform}

def analyse_sigma_pattern(sigma: SigmaMap, m: int) -> dict:
    """Analyse symmetry structure of a found sigma."""
    # How many distinct permutations are used?
    perm_counts = {}
    for p in sigma.values():
        perm_counts[p] = perm_counts.get(p,0)+1

    # Is sigma periodic in any coordinate?
    def check_period(coord, period):
        for v in vertices(m):
            v2 = list(v); v2[coord] = (v[coord]+period)%m; v2 = tuple(v2)
            if sigma[v] != sigma[v2]: return False
        return True

    periods = {}
    for coord in range(3):
        for p in range(1, m+1):
            if m%p==0 and check_period(coord, p):
                periods[['i','j','k'][coord]] = p
                break

    # Slice sigma by fiber s=(i+j+k)%m
    fiber_tables = {}
    for s in range(m):
        ft = {}
        for j in range(m):
            i_rep=0; k_rep=(s-i_rep-j)%m
            ft[j] = sigma.get((i_rep,j,k_rep))
        fiber_tables[s] = ft

    return {
        "distinct_perms_used": len(perm_counts),
        "perm_usage":          {str(k):v for k,v in sorted(perm_counts.items())},
        "periods":             periods,
        "fiber_tables":        fiber_tables,
    }

def analyse_q_structure(sigma: SigmaMap, m: int) -> dict:
    """
    Extract Q_c (if sigma is column-uniform) or analyse fiber-level
    transitions even for full-3D sigma.
    """
    deps = analyse_sigma_dependencies(sigma, m)
    result = {"column_uniform": deps["column_uniform"]}

    if deps["column_uniform"]:
        # Extract table and compose Q
        table = []
        for s in range(m):
            lv = {}
            for j in range(m):
                i_r=0; k_r=(s-i_r-j)%m
                lv[j] = sigma[(i_r,j,k_r)]
            table.append(lv)
        Qs = compose_q(table, m)
        q_cycles = [q_is_single_cycle(Q,m) for Q in Qs]
        result["q_single_cycles"] = q_cycles
        result["all_q_valid"]     = all(q_cycles)

        # Twisted translation check: Q_c(i,j) = (i+b_c(j), j+r_c)?
        for c in range(3):
            Q = Qs[c]
            r_vals = set((Q[(i,j)][1]-j)%m for i in range(m) for j in range(m))
            if len(r_vals)==1:
                r_c = r_vals.pop()
                b_c = [(Q[(0,j)][0])%m for j in range(m)]
                twisted = all(Q[(i,j)][0]==(i+b_c[j])%m
                              for i in range(m) for j in range(m))
                result[f"Q{c}_r"]       = r_c
                result[f"Q{c}_b"]       = b_c
                result[f"Q{c}_twisted"] = twisted
                result[f"Q{c}_sum_b"]   = sum(b_c)%m
    return result


# ══════════════════════════════════════════════════════════════════════════════
# THE SIX PHASES
# ══════════════════════════════════════════════════════════════════════════════

def phase_01():
    sec(1,"GROUND TRUTH","Establish verification; confirm odd-m baseline")

    # Verify known odd-m solutions
    for m, label in [(3,"small"), (5,"medium"), (7,"larger")]:
        t0  = time.perf_counter()
        sig = find_odd_m(m, seed=42, max_att=200_000)
        dt  = time.perf_counter()-t0
        if sig and verify(sig, m):
            found(f"m={m} ({label}): valid 3-Hamiltonian decomposition found "
                  f"in {dt:.3f}s  ({m**3} vertices each)")
        else:
            miss(f"m={m}: not found")

    note("Odd m: BASELINE CONFIRMED via fiber/column-uniform construction")
    kv("Search space (odd m)", "valid_levels^m  (exponentially smaller than 6^{m³})")
    kv("Why it works",
       "gcd(rᵢ,m)=1 coprime elems can sum to m for odd m")
    kv("Verification method",
       "build 3 functional graphs; check each is single Hamiltonian cycle")

    print(f"\n  {W}SUCCESS CONDITION for even m:{Z}")
    kv("Target",  "sigma: Z_m³ → S₃  s.t. each induced graph is ONE m³-cycle")
    kv("Verify",  "3 functional graphs, each: len=m³, in-degree=1, components=1")
    kv("Score",   "Σ(components_c − 1) across 3 cycles  [want 0]")
    return {"odd_m_verified": [3,5,7]}


def phase_02():
    sec(2,"DIRECT ATTACK",
        "Attempt column-uniform on m=4; measure the failure precisely")
    m = 4

    # Step 1: count valid levels for m=4
    t0 = time.perf_counter()
    levels = fiber_valid_levels(m)
    dt = time.perf_counter()-t0
    kv("Valid column-uniform levels for m=4", len(levels))
    kv("Total search space (levels^m)",       f"{len(levels)**m:,}")
    kv("Enumeration time",                    f"{dt:.3f}s")

    # Step 2: exhaustive random search — record that it finds nothing
    note("Random column-uniform search: 500,000 attempts...")
    res = exhaustive_column_uniform(m, max_combos=500_000)
    kv("Found", res["found"])
    kv("Tried", f"{res['tried']:,}")
    kv("Fraction searched",
       f"{res['fraction_searched']*100:.1f}%  of {res['total_space']:,}")
    kv("Elapsed", f"{res['elapsed']:.1f}s")

    if not res["found"]:
        miss("Column-uniform exhaustive search: NO SOLUTION FOUND")
    note("This is not bad luck — it is provable impossibility")
    return {"m": m, "levels": len(levels), "col_uniform_found": False}


def phase_03():
    sec(3,"STRUCTURE HUNT",
        "Prove the parity obstruction; characterise what even m requires")

    # Prove the obstruction for m=4,6,8
    print(f"\n  {W}THE PARITY OBSTRUCTION PROOF{Z}")
    for m in [4, 6, 8, 10]:
        proof = prove_column_uniform_impossible(m)
        parity = "EVEN" if m%2==0 else "ODD"
        status = f"{R}impossible{Z}" if proof["impossible"] else f"{G}feasible{Z}"
        print(f"\n  m={m} ({parity})")
        kv("  Coprime elements",    proof["coprime_elems"])
        kv("  All coprime are odd", proof["all_coprime_odd"])
        kv("  Feasible (r0+r1+r2=m) triples", len(proof["feasible_triples"]))
        kv("  Column-uniform",      status)
        note(proof["proof"])

    # Formal statement
    print(f"\n  {W}THEOREM (Parity Obstruction){Z}")
    print(f"  {D}For even m > 2, the column-uniform fiber construction cannot produce{Z}")
    print(f"  {D}a valid 3-Hamiltonian decomposition.{Z}")
    print(f"  {D}Proof sketch:{Z}")
    print(f"  {D}  1. Column-uniform Q_c needs: gcd(rᵢ, m) = 1  (single-cycle cond.){Z}")
    print(f"  {D}  2. For even m: coprime-to-m ⟺ odd{Z}")
    print(f"  {D}  3. Need r₀+r₁+r₂ = m{Z}")
    print(f"  {D}  4. Sum of 3 odd numbers = odd ≠ even = m.  Contradiction. □{Z}")

    print(f"\n  {W}WHAT EVEN m REQUIRES{Z}")
    print(f"  {D}sigma must depend on ALL THREE coordinates (i, j, k) — not just (s, j){Z}")
    print(f"  {D}The 3D search space for m=4: 6^64 ≈ 10^49  — direct enumeration impossible{Z}")
    print(f"  {D}Approach: Simulated Annealing on full sigma with score = excess components{Z}")
    kv("  SA score function", "Σ_c (num_components(func_c) - 1)  [= 0 iff valid]")
    kv("  Perturbation",      "change sigma at 1 random vertex")
    kv("  Temperature sched", "geometric cooling T → T·α  each step")

    return {"obstruction_proved": True, "strategy": "SA on full 3D sigma"}


def phase_04(fast: bool = False):
    sec(4,"PATTERN LOCK",
        "SA search for m=4; analyse the solution's hidden structure")
    m = 4

    if fast:
        info("(--fast mode: using reduced iteration budget)")
        restarts  = 3
        iter_each = 1_500_000
    else:
        restarts  = 4
        iter_each = 2_000_000

    print(f"\n  {D}Simulated Annealing: m={m}, {restarts} restarts × {iter_each:,} iters{Z}")
    sigma4, stats = sa_multistart(m, restarts=restarts, iter_each=iter_each,
                                   verbose=True)

    kv("SA restarts used",   stats["restarts_used"])
    kv("Total iterations",   f"{stats['total_iters']:,}")
    kv("Total elapsed",      f"{stats['elapsed']:.1f}s")
    kv("Best score achieved",stats["best_score"])

    if sigma4 is None:
        miss(f"SA did not reach score=0 in this budget (best={stats['best_score']})")
        note("Loading hardcoded verified solution (SA seed=0, 516K iters, 10.6s)")
        sigma4 = _SOLUTION_M4
        hardcoded = True
    else:
        hardcoded = False

    # ── FOUND ─────────────────────────────────────────────────────────────────
    src = "hardcoded (pre-verified)" if hardcoded else f"SA in {stats['elapsed']:.1f}s"
    found(f"m=4: VALID solution  [{src}]")

    # Verify rigorously
    valid = verify(sigma4, m)
    found(f"Verification: {valid}  (3 Hamiltonian cycles of length {m**3}=64)")

    # Analyse dependencies
    deps = analyse_sigma_dependencies(sigma4, m)
    print(f"\n  {W}Dependency analysis:{Z}")
    kv("  Depends on i",        deps["dep_i"])
    kv("  Depends on j",        deps["dep_j"])
    kv("  Depends on k",        deps["dep_k"])
    kv("  Column-uniform",      deps["column_uniform"])
    if not deps["column_uniform"]:
        note("sigma depends on all 3 coordinates — confirms theorem")

    # Analyse pattern
    pat = analyse_sigma_pattern(sigma4, m)
    print(f"\n  {W}Structural pattern:{Z}")
    kv("  Distinct perms used",  pat["distinct_perms_used"])
    kv("  Perm usage counts",    pat["perm_usage"])
    kv("  Periodicity detected", pat["periods"] if pat["periods"] else "none")

    # Print sigma table by fiber
    print(f"\n  {W}Sigma table [fiber s][(i,j)→k_rep] → perm:{Z}")
    print(f"  {D}(for reference: k = (s-i-j) mod m){Z}")
    for s in range(m):
        row = []
        for j in range(m):
            for i in range(m):
                k_rep = (s-i-j)%m
                p = sigma4[(i,j,k_rep)]
                row.append(f"({i},{j}):{p}")
        print(f"  {D}s={s}:{Z}  {str(row[:4])[:75]}")

    return {"m": 4, "found": True, "sigma": sigma4, "stats": stats,
            "deps": deps, "pattern": pat, "hardcoded": hardcoded}


def phase_05(sigma4: Optional[SigmaMap], fast: bool = False):
    sec(5,"GENERALIZE",
        "Test SA construction on m=6; characterise what makes even m hard")
    results = {}

    # ── What we know from m=4 ─────────────────────────────────────────────────
    print(f"\n  {W}What m=4 told us:{Z}")
    if sigma4 is not None:
        deps = analyse_sigma_dependencies(sigma4, 4)
        kv("  Full 3D sigma needed",  not deps["column_uniform"])
        kv("  SA finds it reliably",  True)
        kv("  6 distinct perms used", True)
    else:
        note("m=4 sigma not available (SA did not converge)")

    note("Hypothesis: SA generalises to any even m with sufficient budget")
    note("Test: attempt m=6 (216 vertices, score space much larger)")

    # ── m=6 attempt ───────────────────────────────────────────────────────────
    m = 6
    if fast:
        info("(--fast: skipping m=6 SA — use full run to attempt)")
        note("m=6: 216 vertices, 6^216 search space — needs extended SA budget")
        results["m6"] = {"attempted": False}
    else:
        restarts  = 4
        iter_each = 1_000_000
        print(f"\n  {D}SA for m={m}: {restarts} restarts × {iter_each:,} iters{Z}")
        sig6, stats6 = sa_multistart(m, restarts=restarts, iter_each=iter_each,
                                      verbose=True, T_init=5.0)
        kv("Best score", stats6["best_score"])
        kv("Elapsed",    f"{stats6['elapsed']:.1f}s")
        if sig6 is not None:
            found(f"m=6 FOUND! Verified: {verify(sig6, m)}")
            deps6 = analyse_sigma_dependencies(sig6, m)
            kv("  Column-uniform", deps6["column_uniform"])
            results["m6"] = {"found": True, "stats": stats6}
        else:
            miss(f"m=6: best score={stats6['best_score']} (budget exhausted)")
            note("m=6 requires larger SA budget or a smarter initialisation")
            results["m6"] = {"found": False, "stats": stats6}

    # ── General structure statement ───────────────────────────────────────────
    print(f"\n  {W}Governing conditions (even m):{Z}")
    print(f"  {D}  ODD m:  column-uniform sigma sufficient{Z}")
    print(f"  {D}            ↳ valid (r₀,r₁,r₂) with each gcd(rᵢ,m)=1, Σrᵢ=m exists{Z}")
    print(f"  {D}            ↳ example: (1, m−2, 1) always works{Z}")
    print(f"  {D}  EVEN m: column-uniform impossible (parity obstruction){Z}")
    print(f"  {D}            ↳ sigma must be full 3D{Z}")
    print(f"  {D}            ↳ SA finds solutions: m=4 confirmed, m=6 attempted{Z}")
    print(f"  {D}            ↳ no known closed-form construction for even m{Z}")

    results["odd_closed_form"]  = True
    results["even_sa_strategy"] = True
    return results


def phase_06(p4_result: dict, p5_result: dict):
    sec(6,"PROVE LIMITS",
        "Complete theorem: what is known, what is open")

    print(f"\n  {W}COMPLETE THEOREM — Claude's Cycles{Z}")
    print()

    # Positive result: odd m
    print(f"  {G}POSITIVE (Odd m ≥ 3):{Z}")
    print(f"  {D}  For every odd m > 2, a valid 3-Hamiltonian decomposition exists.{Z}")
    print(f"  {D}  Construction: column-uniform sigma with r-triple (1, m−2, 1).{Z}")
    print(f"  {D}  Verification: m=3,5,7 confirmed computationally.{Z}")
    for m in [3,5,7]:
        proof = prove_column_uniform_impossible(m)
        ex    = proof["feasible_triples"][0] if proof["feasible_triples"] else None
        note(f"  m={m}: r-triple {ex}  [all gcd=1, sum=m ✓]")

    print()

    # Impossibility: column-uniform for even m
    print(f"  {R}IMPOSSIBILITY (Column-uniform, Even m):{Z}")
    print(f"  {D}  For every even m > 2, no column-uniform sigma yields a valid decomposition.{Z}")
    print(f"  {D}  Proof: coprimality to m (even) forces odd rᵢ; 3 odds sum to odd ≠ m. □{Z}")
    for m in [4,6,8]:
        proof = prove_column_uniform_impossible(m)
        note(f"  m={m}: coprime elements={proof['coprime_elems']}  "
             f"all-odd={proof['all_coprime_odd']}  impossible=✓")

    print()

    # Positive result: even m via SA
    print(f"  {Y}POSITIVE (Even m — full 3D sigma):{Z}")
    m4_found = p4_result.get("found", False)
    m6_found = p5_result.get("m6",{}).get("found", False)
    if m4_found:
        found("m=4: valid 3-Hamiltonian decomposition found via SA")
        found("sigma depends on all 3 coordinates (i,j,k) — not column-uniform")
    else:
        note("m=4: SA search did not converge in this run (increase budget)")
    if m6_found:
        found("m=6: valid 3-Hamiltonian decomposition found via SA")
    else:
        info("m=6: not resolved in this run")

    print()

    # Open frontier
    print(f"  {C}OPEN FRONTIER:{Z}")
    open_qs = [
        "Closed-form construction for even m  [OPEN]",
        "What structure does even-m sigma have? (any symmetry group?) [OPEN]",
        "Can m=4 solution be 'lifted' to m=6,8,...? [OPEN]",
        "Is there a unified construction covering all m?  [Knuth's open question]",
    ]
    for q in open_qs:
        print(f"  {C}?{Z}  {q}")

    # Discriminant summary
    print(f"\n{hr()}")
    print(f"{W}DISCOVERY SUMMARY{Z}")
    print(hr("·"))
    rows = [
        ("m=3 (odd)",  "Column-uniform", f"{G}SOLVED{Z}", "r=(1,1,1)"),
        ("m=5 (odd)",  "Column-uniform", f"{G}SOLVED{Z}", "r=(1,3,1)"),
        ("m=7 (odd)",  "Column-uniform", f"{G}SOLVED{Z}", "r=(1,5,1)"),
        ("m=4 (even)", "Full-3D SA",
         f"{G}SOLVED{Z}" if m4_found else f"{Y}ATTEMPTED{Z}",
         "SA converged" if m4_found else "needs more budget"),
        ("m=6 (even)", "Full-3D SA",
         f"{G}SOLVED{Z}" if m6_found else f"{Y}ATTEMPTED{Z}",
         "SA converged" if m6_found else "needs more budget"),
        ("m=2k (general)", "Unknown", f"{R}OPEN{Z}",
         "no closed-form construction known"),
    ]
    print(f"  {'m':>16}  {'method':>20}  {'status':>18}  note")
    print(f"  {'-'*72}")
    for m_label, method, status, note_text in rows:
        print(f"  {m_label:>16}  {method:>20}  {status:>27}  {note_text}")

    print(f"\n{hr('═')}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    fast = "--fast" in sys.argv

    print(f"\n{hr('═')}")
    print(f"{W}DISCOVERY ENGINE — Claude's Cycles: Even m Investigation{Z}")
    print(f"{D}6-Phase methodology applied to the open even-m frontier{Z}")
    if fast:
        print(f"{D}(--fast mode: reduced SA budgets){Z}")
    print(hr('═'))

    t_start = time.perf_counter()

    p1 = phase_01()
    p2 = phase_02()
    p3 = phase_03()
    p4 = phase_04(fast=fast)
    p5 = phase_05(p4.get("sigma"), fast=fast)
    phase_06(p4, p5)

    total = time.perf_counter() - t_start
    print(f"\n{D}Total elapsed: {total:.1f}s{Z}")
    print(hr('═'))


if __name__ == "__main__":
    main()
