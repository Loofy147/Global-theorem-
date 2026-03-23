"""
analysis.py — Automated mathematical analysis of Claude's Cycles solutions.

Given a sigma function or SigmaTable, this module:

1. STRUCTURAL ANALYSIS
   - Detects column-uniformity (does sigma depend only on s,j or all of i,j,k?)
   - Computes the Q_c composed permutations
   - Identifies the twisted translation form Q_c(i,j) = (i+b_c(j), j+r_c)

2. THEOREM VERIFICATION
   - Theorem 1: Twisted Translation Structure (auto-detected)
   - Theorem 2: Single-Cycle Conditions (gcd checks)
   - Theorem 3: Existence for odd m (constructive verification)
   - Theorem 4: Impossibility for even m (parity argument)

3. PATTERN REPORTING
   - Full solution tables
   - Arc sequences for each Hamiltonian cycle
   - Comparison across m values
"""

from __future__ import annotations
from typing import Optional, List, Dict, Tuple
from math import gcd

from .core import (
    Vertex, Perm, SigmaFn,
    build_functional_graphs, verify_sigma, VerifyResult,
    trace_cycle, arc_sequence, vertices
)
from .fiber import (
    SigmaTable, compose_levels, analyze_Q_structure,
    even_m_impossibility_check, verify_single_cycle_conditions,
    table_to_sigma_fn, FIBER_SHIFTS
)


# =========================================================================== #
# Structural analysis of sigma
# =========================================================================== #

def detect_dependencies(sigma: SigmaFn, m: int) -> Dict[str, bool]:
    """
    Determine which coordinates sigma actually depends on.
    Returns {'i': bool, 'j': bool, 'k': bool, 's': bool}
    where s = (i+j+k) mod m.
    """
    depends_i = depends_j = depends_k = False
    for i in range(m):
        for j in range(m):
            for k in range(m):
                base = sigma(i, j, k)
                if i > 0 and sigma(i, j, k) != sigma(0, j, k):
                    depends_i = True
                if j > 0 and sigma(i, j, k) != sigma(i, 0, k):
                    depends_j = True
                if k > 0 and sigma(i, j, k) != sigma(i, j, 0):
                    depends_k = True

    # Check if sigma depends only on s=(i+j+k)%m and j
    depends_s_only = True
    for i in range(m):
        for j in range(m):
            for k in range(m):
                s = (i + j + k) % m
                # Find another vertex with same s and j but different i
                other_i = (i + 1) % m
                other_k = (s - other_i - j) % m
                if sigma(i, j, k) != sigma(other_i, j, other_k):
                    depends_s_only = False
                    break
            if not depends_s_only:
                break
        if not depends_s_only:
            break

    return {
        "i": depends_i,
        "j": depends_j,
        "k": depends_k,
        "column_uniform": depends_s_only,   # sigma(i,j,k) = f(s,j)
    }


def extract_sigma_table(sigma: SigmaFn, m: int) -> Optional[SigmaTable]:
    """
    If sigma is column-uniform (depends only on s,j), extract SigmaTable.
    Returns None if sigma is not column-uniform.
    """
    deps = detect_dependencies(sigma, m)
    if not deps["column_uniform"]:
        return None
    table = []
    for s in range(m):
        level = {}
        for j in range(m):
            # Find a representative vertex in fiber s with column j
            i_rep = 0
            k_rep = (s - i_rep - j) % m
            level[j] = list(sigma(i_rep, j, k_rep))
        table.append(level)
    return table


# =========================================================================== #
# Full solution analysis
# =========================================================================== #

class SolutionAnalysis:
    """
    Comprehensive analysis of a Claude's Cycles solution.

    Usage:
        analysis = SolutionAnalysis(sigma_fn, m=5)
        analysis.run()
        print(analysis.report())
    """

    def __init__(self, sigma: SigmaFn, m: int):
        self.sigma = sigma
        self.m = m
        self._run = False

    def run(self) -> "SolutionAnalysis":
        m = self.m
        sigma = self.sigma

        # 1. Core verification
        self.verify_result: VerifyResult = verify_sigma(sigma, m)

        # 2. Build functional graphs and traces
        self.funcs = build_functional_graphs(sigma, m)
        self.cycle_paths = [trace_cycle(fg, m) for fg in self.funcs]
        self.arc_seqs = [arc_sequence(p, m) for p in self.cycle_paths]

        # 3. Structural dependencies
        self.deps = detect_dependencies(sigma, m)

        # 4. If column-uniform, extract Q and analyze
        self.sigma_table: Optional[SigmaTable] = extract_sigma_table(sigma, m)
        if self.sigma_table is not None:
            Qs = compose_levels(self.sigma_table, m)
            self.Q_analysis: Optional[dict] = analyze_Q_structure(Qs, m)
        else:
            self.Q_analysis = None

        # 5. Theoretical checks
        self.impossibility = even_m_impossibility_check(m)

        self._run = True
        return self

    def report(self, verbose: bool = True) -> str:
        if not self._run:
            self.run()
        m = self.m
        lines = [
            "=" * 64,
            f"CLAUDE'S CYCLES SOLUTION ANALYSIS — m={m}",
            "=" * 64,
            "",
            f"Verification: {self.verify_result}",
            "",
        ]

        # Dependency structure
        d = self.deps
        dep_str = "sigma depends on: " + ", ".join(
            x for x, v in [("i",d["i"]),("j",d["j"]),("k",d["k"])] if v
        )
        if d["column_uniform"]:
            dep_str += "  →  COLUMN-UNIFORM  (only s=(i+j+k)%m and j)"
        lines.append(dep_str)
        lines.append("")

        # Sigma table
        if self.sigma_table is not None and verbose:
            lines.append("Sigma table  [s][j] → [arc₀→cycle, arc₁→cycle, arc₂→cycle]:")
            for s in range(m):
                row = [self.sigma_table[s][j] for j in range(m)]
                lines.append(f"  s={s}: {row}")
            lines.append("")

        # Arc sequences
        lines.append("Hamiltonian cycle arc sequences (I=incr_i, J=incr_j, K=incr_k):")
        for c in range(3):
            seq = self.arc_seqs[c]
            counts = {x: seq.count(x) for x in "IJK"}
            lines.append(f"  Cycle {c}: {seq[:40]}{'...' if len(seq)>40 else ''}"
                         f"  [I:{counts['I']} J:{counts['J']} K:{counts['K']}]")
        lines.append("")

        # Q structure
        if self.Q_analysis is not None:
            qa = self.Q_analysis
            lines.append("Composed fiber permutation Q_c:")
            twisted_str = "✅ YES" if qa["all_twisted"] else "❌ NO"
            lines.append(f"  Twisted translation form Q_c(i,j)=(i+b_c(j),j+r_c): {twisted_str}")
            if qa["all_twisted"]:
                lines.append(f"  r-values: {qa['r_values']}  sum={qa['sum_r']} (= m? {qa['sum_r']==m})")
            for info in qa["cycles"]:
                c = info["cycle"]
                if info["is_twisted"]:
                    sc = verify_single_cycle_conditions(info["r_c"], info["b_c"], m)
                    lines.append(
                        f"  Q_{c}: r={info['r_c']} b={info['b_c']}"
                        f"  Σb={info['sum_b']}"
                        f"  cond_a(gcd(r,m)=1)={'✅' if sc['condition_a'] else '❌'}"
                        f"  cond_b(gcd(Σb,m)=1)={'✅' if sc['condition_b'] else '❌'}"
                        f"  single_cycle={'✅' if info['is_single_cycle'] else '❌'}"
                    )
                else:
                    lines.append(f"  Q_{c}: NOT in twisted form")
            lines.append("")

        # Theoretical context
        imp = self.impossibility
        lines.append(f"Theoretical context (m={m}):")
        if imp["m_is_even"]:
            lines.append(f"  m={m} is EVEN → column-uniform fiber construction IMPOSSIBLE")
            lines.append(f"  (Proof: {imp['proof']})")
        else:
            lines.append(f"  m={m} is ODD → column-uniform fiber construction POSSIBLE")
            ex = imp.get("example")
            if ex:
                lines.append(f"  Example valid (r₀,r₁,r₂) = {ex}")

        lines.append("=" * 64)
        return "\n".join(lines)

    def __repr__(self) -> str:
        status = "✅" if (self._run and self.verify_result.is_valid) else "?"
        return f"SolutionAnalysis(m={self.m}, valid={status})"


# =========================================================================== #
# Cross-m comparison
# =========================================================================== #

def compare_across_m(results: Dict[int, "SolutionAnalysis"]) -> str:
    """
    Generate a comparison table across multiple m values.
    results: {m: SolutionAnalysis}
    """
    lines = [
        "=" * 72,
        "COMPARISON ACROSS m VALUES",
        "=" * 72,
        f"{'m':>4}  {'parity':>6}  {'valid':>7}  {'col_unif':>9}  "
        f"{'twisted':>8}  {'r_vals':>20}",
        "-" * 72,
    ]
    for m in sorted(results):
        a = results[m]
        if not a._run:
            a.run()
        parity = "ODD" if m % 2 == 1 else "EVEN"
        valid = "✅" if a.verify_result.is_valid else "❌"
        col = "✅" if a.deps["column_uniform"] else "❌"
        if a.Q_analysis:
            twisted = "✅" if a.Q_analysis["all_twisted"] else "❌"
            r = str(a.Q_analysis.get("r_values", "—"))
        else:
            twisted = "—"
            r = "—"
        lines.append(f"{m:>4}  {parity:>6}  {valid:>7}  {col:>9}  {twisted:>8}  {r:>20}")
    lines.append("=" * 72)
    return "\n".join(lines)
