"""
core.py — Claude's Cycles: Digraph definition and verification primitives.

The digraph G_m:
  - Vertices: (i,j,k)  for 0 <= i,j,k < m
  - Arcs: each vertex has 3 outgoing arcs:
      arc 0: (i,j,k) → (i+1 mod m, j, k)   [increment i]
      arc 1: (i,j,k) → (i, j+1 mod m, k)   [increment j]
      arc 2: (i,j,k) → (i, j, k+1 mod m)   [increment k]

A sigma function assigns each arc to one of 3 "colors" (cycles 0,1,2).
A valid decomposition: each color class is a single directed Hamiltonian cycle.
"""

from __future__ import annotations
from typing import Callable, Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from math import gcd

# --------------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------------- #

Vertex   = Tuple[int, int, int]          # (i, j, k)
Perm     = List[int]                     # [c0, c1, c2]: arc_type t → cycle c_t
SigmaFn  = Callable[[int, int, int], Perm]
FuncGraph = Dict[Vertex, Vertex]         # functional digraph for one cycle

ARC_SHIFTS: Tuple[Vertex, ...] = (
    (1, 0, 0),  # arc 0: incr i
    (0, 1, 0),  # arc 1: incr j
    (0, 0, 1),  # arc 2: incr k
)

ARC_NAMES = ("I", "J", "K")


# --------------------------------------------------------------------------- #
# Digraph
# --------------------------------------------------------------------------- #

def vertices(m: int) -> List[Vertex]:
    return [(i, j, k) for i in range(m) for j in range(m) for k in range(m)]


def arc_target(v: Vertex, arc_type: int, m: int) -> Vertex:
    s = ARC_SHIFTS[arc_type]
    return ((v[0]+s[0])%m, (v[1]+s[1])%m, (v[2]+s[2])%m)


def build_functional_graphs(sigma: SigmaFn, m: int) -> List[FuncGraph]:
    """Build 3 functional digraphs from sigma."""
    funcs: List[FuncGraph] = [{}, {}, {}]
    for v in vertices(m):
        perm = sigma(*v)
        for arc_type, cycle in enumerate(perm):
            funcs[cycle][v] = arc_target(v, arc_type, m)
    return funcs


# --------------------------------------------------------------------------- #
# Verification
# --------------------------------------------------------------------------- #

@dataclass
class VerifyResult:
    m: int
    is_valid: bool
    cycle_lengths: List[int]           # length of each component (want [m³,m³,m³])
    component_counts: List[int]        # num components per color (want [1,1,1])
    errors: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        if self.is_valid:
            return f"✅ m={self.m}: Valid 3-Hamiltonian decomposition (each cycle length={self.m**3})"
        summary = f"❌ m={self.m}: INVALID — " + "; ".join(self.errors)
        return summary


def verify_functional_graph(fg: FuncGraph, m: int) -> Tuple[bool, int]:
    """Return (is_single_hamiltonian_cycle, largest_component_length)."""
    n = m**3
    if len(fg) != n:
        return False, len(fg)
    visited: set = set()
    # Check every connected component
    components = []
    for start in fg:
        if start in visited:
            continue
        cur, length = start, 0
        while cur not in visited:
            visited.add(cur)
            cur = fg[cur]
            length += 1
        components.append(length)
    return len(components) == 1, max(components) if components else 0


def verify_sigma(sigma: SigmaFn, m: int) -> VerifyResult:
    """Full verification of a sigma function."""
    funcs = build_functional_graphs(sigma, m)
    n = m**3
    errors = []

    # Check out-degree = 1 per vertex per cycle
    for c, fg in enumerate(funcs):
        if len(fg) != n:
            errors.append(f"cycle {c} has {len(fg)} arcs (expected {n})")

    # Check in-degree = 1 (= each vertex is hit exactly once)
    for c, fg in enumerate(funcs):
        in_deg: Dict[Vertex, int] = {}
        for nb in fg.values():
            in_deg[nb] = in_deg.get(nb, 0) + 1
        bad = [v for v, d in in_deg.items() if d != 1]
        if bad:
            errors.append(f"cycle {c}: {len(bad)} vertices with in-degree ≠ 1")

    cycle_lengths = []
    component_counts = []
    for c, fg in enumerate(funcs):
        single, max_len = verify_functional_graph(fg, m)
        visited: set = set()
        comps = 0
        for start in fg:
            if start not in visited:
                comps += 1
                cur = start
                while cur not in visited:
                    visited.add(cur)
                    cur = fg[cur]
        component_counts.append(comps)
        cycle_lengths.append(max_len)
        if not single:
            errors.append(f"cycle {c}: {comps} components (not Hamiltonian)")

    return VerifyResult(
        m=m,
        is_valid=(len(errors) == 0),
        cycle_lengths=cycle_lengths,
        component_counts=component_counts,
        errors=errors,
    )


# --------------------------------------------------------------------------- #
# Cycle tracing
# --------------------------------------------------------------------------- #

def trace_cycle(fg: FuncGraph, m: int) -> List[Vertex]:
    """Trace the Hamiltonian cycle path starting from (0,0,0)."""
    start = (0, 0, 0)
    path = []
    cur = start
    visited: set = set()
    while cur not in visited:
        path.append(cur)
        visited.add(cur)
        cur = fg[cur]
    return path


def arc_sequence(path: List[Vertex], m: int) -> str:
    """Return string of arc types: I/J/K."""
    n = len(path)
    result = []
    for step in range(n):
        v1, v2 = path[step], path[(step+1) % n]
        diff = tuple((v2[d]-v1[d]) % m for d in range(3))
        idx = ARC_SHIFTS.index(diff) if diff in ARC_SHIFTS else -1
        result.append(ARC_NAMES[idx] if idx >= 0 else "?")
    return "".join(result)
