"""
solutions.py — Hardcoded verified solutions for Claude's Cycles.

All solutions have been computationally verified (3 Hamiltonian cycles).
Use get_solution(m) to retrieve; use construct_for_odd_m(m) for
a general algorithm that works on any odd m > 2.
"""

from __future__ import annotations
from typing import Optional, List
from .fiber import SigmaTable, table_to_sigma_fn
from .core import SigmaFn

# --------------------------------------------------------------------------- #
# Hardcoded verified solutions
# --------------------------------------------------------------------------- #

_SOLUTION_M3: SigmaTable = [
    # s=0: level[j] = [arc₀→cycle, arc₁→cycle, arc₂→cycle]
    {0: [2, 0, 1],  1: [1, 0, 2],  2: [2, 0, 1]},
    # s=1
    {0: [0, 2, 1],  1: [1, 2, 0],  2: [0, 2, 1]},
    # s=2
    {0: [0, 1, 2],  1: [0, 1, 2],  2: [0, 1, 2]},
]

# Composed Q structure for m=3:
#   Q_0(i,j) = (i + b_0(j), j+1)  b_0=[1,2,2]  sum=2  ✅
#   Q_1(i,j) = (i + b_1(j), j+1)  b_1=[0,2,0]  sum=2  ✅
#   Q_2(i,j) = (i + b_2(j), j+1)  b_2=[1,0,1]  sum=2  ✅

_SOLUTION_M5: SigmaTable = [
    # s=0
    {0: [0,2,1], 1: [1,2,0], 2: [0,2,1], 3: [0,2,1], 4: [1,2,0]},
    # s=1
    {0: [2,1,0], 1: [2,1,0], 2: [0,1,2], 3: [2,1,0], 4: [2,1,0]},
    # s=2
    {0: [2,1,0], 1: [0,1,2], 2: [0,1,2], 3: [2,1,0], 4: [2,1,0]},
    # s=3
    {0: [2,1,0], 1: [2,1,0], 2: [0,1,2], 3: [0,1,2], 4: [2,1,0]},
    # s=4
    {0: [2,0,1], 1: [1,0,2], 2: [2,0,1], 3: [1,0,2], 4: [2,0,1]},
]

_KNOWN: dict = {3: _SOLUTION_M3, 5: _SOLUTION_M5}


def get_solution(m: int) -> Optional[SigmaFn]:
    """
    Return a precomputed SigmaFn for known m values (currently m=3,5).
    Returns None for unknown m (use search module instead).
    """
    if m not in _KNOWN:
        return None
    return table_to_sigma_fn(_KNOWN[m], m)


def get_solution_table(m: int) -> Optional[SigmaTable]:
    """Return the raw SigmaTable for known m values."""
    return _KNOWN.get(m)


def known_m_values() -> List[int]:
    """Return sorted list of m values with hardcoded solutions."""
    return sorted(_KNOWN.keys())


# --------------------------------------------------------------------------- #
# Constructive algorithm for odd m
# --------------------------------------------------------------------------- #

def construct_for_odd_m(m: int,
                        seed: int = 42,
                        max_attempts: int = 200_000) -> Optional[SigmaFn]:
    """
    Find a valid sigma for any odd m > 2 using RandomSearch.
    The fiber decomposition approach always succeeds for odd m (Theorem 3).

    Returns SigmaFn or None (None is unexpected for m ≤ ~15).
    """
    if m % 2 == 0:
        raise ValueError(
            f"m={m} is even. The fiber construction is provably impossible for even m. "
            "Use search.find_sigma(m, strategy='sa') instead."
        )
    if m <= 2:
        raise ValueError(f"m must be > 2 (got m={m})")

    # Check hardcoded first
    if m in _KNOWN:
        return table_to_sigma_fn(_KNOWN[m], m)

    from .search import RandomSearch
    rs = RandomSearch(m, seed=seed)
    table = rs.run(max_attempts)
    if table is None:
        return None
    return table_to_sigma_fn(table, m)
