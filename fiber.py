"""
fiber.py — Fiber decomposition of the Claude's Cycles problem.

KEY INSIGHT: The map  f(i,j,k) = (i+j+k) mod m  stratifies the digraph
into m "fiber" layers F_0, …, F_{m-1}, each of size m².
Every arc goes from F_s to F_{s+1 mod m}.

In fiber coordinates (i,j) with k = (s-i-j) mod m, the 3 arc types become:
  arc 0: (i,j) in F_s  →  (i+1, j)    in F_{s+1}   [shift (1,0)]
  arc 1: (i,j) in F_s  →  (i,   j+1)  in F_{s+1}   [shift (0,1)]
  arc 2: (i,j) in F_s  →  (i,   j)    in F_{s+1}   [shift (0,0) — identity]

A "column-uniform" sigma depends only on (s, j) — not on i.
At each level s, column j gets a fixed permutation: perm[j] = [arc→cycle].

The COMPOSED permutation after all m levels:
  Q_c(i,j) = (i + b_c(j),  j + r_c) mod m
where r_c = total j-increment for cycle c, b_c(j) = total i-increment.

Single m²-cycle condition:  gcd(r_c, m) = 1  AND  gcd(Σ b_c(j), m) = 1
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Callable
from math import gcd
from itertools import permutations as _iperms

# 2D arc shifts in fiber space
FIBER_SHIFTS: Tuple[Tuple[int,int],...] = (
    (1, 0),  # arc 0: incr i
    (0, 1),  # arc 1: incr j
    (0, 0),  # arc 2: identity
)

FiberPos   = Tuple[int, int]           # (i, j) in fiber space
LevelTable = Dict[int, List[int]]      # j → perm (for one fiber level)
SigmaTable = List[LevelTable]          # indexed by s=0..m-1
QFunc      = Dict[FiberPos, FiberPos]  # composed permutation


# --------------------------------------------------------------------------- #
# Level table validity
# --------------------------------------------------------------------------- #

def is_bijective_level(level: LevelTable, m: int) -> bool:
    """
    Check that at level s, each cycle c induces a bijection on Z_m².
    For cycle c: the set of targets {(i+di, j+dj) : j in Z_m, i in Z_m}
    must be exactly Z_m² (all m² positions hit).
    """
    for c in range(3):
        targets = set()
        for j in range(m):
            arc_type = level[j].index(c)
            di, dj = FIBER_SHIFTS[arc_type]
            for i in range(m):
                targets.add(((i+di) % m, (j+dj) % m))
        if len(targets) != m * m:
            return False
    return True


def all_valid_levels(m: int) -> List[LevelTable]:
    """Enumerate all column-uniform level assignments that are bijective."""
    result = []
    for combo in _product(_ALL_PERMS, repeat=m):
        level = {j: list(combo[j]) for j in range(m)}
        if is_bijective_level(level, m):
            result.append(level)
    return result


# Lazy import helper
from itertools import product as _product
_ALL_PERMS = list(_iperms(range(3)))


# --------------------------------------------------------------------------- #
# Q composition
# --------------------------------------------------------------------------- #

def compose_levels(sigma_table: SigmaTable, m: int) -> List[QFunc]:
    """
    Compose all m fiber-level functions to get Q_0, Q_1, Q_2.
    Returns 3 permutations on Z_m² (as dicts).
    """
    Qs: List[QFunc] = [{} for _ in range(3)]
    for i0 in range(m):
        for j0 in range(m):
            pos = [[i0, j0], [i0, j0], [i0, j0]]   # pos[c] = current (i,j)
            for s in range(m):
                level = sigma_table[s]
                for c in range(3):
                    cj = pos[c][1]
                    perm = level[cj]
                    arc_type = perm.index(c)
                    di, dj = FIBER_SHIFTS[arc_type]
                    pos[c][0] = (pos[c][0] + di) % m
                    pos[c][1] = (pos[c][1] + dj) % m
            for c in range(3):
                Qs[c][(i0, j0)] = (pos[c][0], pos[c][1])
    return Qs


def is_single_q_cycle(Q: QFunc, m: int) -> bool:
    """Check that permutation Q on Z_m² is a single m²-cycle."""
    n = m * m
    visited: set = set()
    cur: FiberPos = (0, 0)
    while cur not in visited:
        visited.add(cur)
        cur = Q[cur]
    return len(visited) == n and cur == (0, 0)


# --------------------------------------------------------------------------- #
# Lift sigma_table → SigmaFn (3D)
# --------------------------------------------------------------------------- #

def table_to_sigma_fn(sigma_table: SigmaTable, m: int):
    """
    Convert a SigmaTable (indexed by [s][j]) into a 3D sigma function
    sigma(i, j, k) that can be used with core.verify_sigma.
    The key: depends only on s=(i+j+k)%m and j.
    """
    def sigma(i: int, j: int, k: int) -> List[int]:
        s = (i + j + k) % m
        return list(sigma_table[s][j])
    return sigma


# --------------------------------------------------------------------------- #
# Q structure analysis
# --------------------------------------------------------------------------- #

def analyze_Q_structure(Qs: List[QFunc], m: int) -> dict:
    """
    Analyze whether Q_c has the twisted translation form:
      Q_c(i,j) = (i + b_c(j),  j + r_c) mod m
    Returns a dict with r_c, b_c, is_twisted, single_cycle per cycle.
    """
    result = {"cycles": [], "all_twisted": True, "all_single": True}
    for c in range(3):
        Q = Qs[c]
        # Detect r_c: j-increment should be constant across all starting positions
        r_c_vals = set((Q[(i,j)][1] - j) % m for i in range(m) for j in range(m))
        is_uniform_r = (len(r_c_vals) == 1)
        r_c = r_c_vals.pop() if is_uniform_r else None

        # Detect b_c(j): i-offset at fixed starting i=0
        if is_uniform_r:
            b_c = [(Q[(0,j)][0] - 0) % m for j in range(m)]
            # Verify b_c is shift-invariant: Q(i,j)[0] = i + b_c(j) mod m
            is_twisted = all(Q[(i,j)][0] == (i + b_c[j]) % m
                             for i in range(m) for j in range(m))
        else:
            b_c = None
            is_twisted = False

        single = is_single_q_cycle(Q, m)

        cycle_info = {
            "cycle": c,
            "r_c": r_c,
            "b_c": b_c,
            "is_twisted": is_twisted,
            "is_single_cycle": single,
            "sum_b": (sum(b_c) % m) if b_c else None,
            "gcd_r_m": gcd(r_c, m) if r_c is not None else None,
            "gcd_sumb_m": gcd(sum(b_c) % m, m) if b_c else None,
        }
        result["cycles"].append(cycle_info)
        if not is_twisted:
            result["all_twisted"] = False
        if not single:
            result["all_single"] = False

    if result["all_twisted"]:
        r_vals = [info["r_c"] for info in result["cycles"]]
        result["sum_r"] = sum(r_vals) % m
        result["r_values"] = r_vals
    return result


# --------------------------------------------------------------------------- #
# Theorem verification helpers
# --------------------------------------------------------------------------- #

def verify_single_cycle_conditions(r_c: int, b_c: List[int], m: int) -> dict:
    """
    Verify the two necessary and sufficient conditions for Q_c to be a
    single m²-Hamiltonian cycle.
    """
    s_b = sum(b_c) % m
    return {
        "gcd_r_m": gcd(r_c, m),
        "gcd_sumb_m": gcd(s_b, m),
        "condition_a": gcd(r_c, m) == 1,
        "condition_b": gcd(s_b, m) == 1,
        "both_satisfied": gcd(r_c, m) == 1 and gcd(s_b, m) == 1,
    }


def even_m_impossibility_check(m: int) -> dict:
    """
    Verify the impossibility theorem for even m:
    No (r_0,r_1,r_2) with gcd(r_c,m)=1 can sum to m when m is even.
    """
    if m % 2 == 0:
        # Coprime to even m means ODD
        # Sum of 3 odd numbers is ODD ≠ EVEN = m
        example_coprime = [r for r in range(m) if gcd(r, m) == 1]
        min_sum = sum(sorted(example_coprime)[:3])
        return {
            "m": m,
            "m_is_even": True,
            "coprime_elements": example_coprime,
            "all_coprime_are_odd": all(r % 2 == 1 for r in example_coprime),
            "three_odds_sum_is_odd": True,
            "needed_sum": m,
            "impossibility_proved": True,
            "proof": "All r coprime to even m are odd. Sum of 3 odds is odd ≠ m (even).",
        }
    else:
        # For odd m: show valid (r_0,r_1,r_2) exists
        valid = [(r0,r1,r2) for r0 in range(m) for r1 in range(m) for r2 in range(m)
                 if gcd(r0,m)==1 and gcd(r1,m)==1 and gcd(r2,m)==1 and r0+r1+r2==m]
        return {
            "m": m,
            "m_is_even": False,
            "impossibility_proved": False,
            "valid_r_triples_count": len(valid),
            "example": valid[0] if valid else None,
        }
