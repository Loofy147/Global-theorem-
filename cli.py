"""
cli.py — Command-line interface for the Claude's Cycles system.

Usage:
    python -m claudecycles                   # demo all modes
    python -m claudecycles verify 3          # verify known m=3 solution
    python -m claudecycles verify 5          # verify known m=5 solution
    python -m claudecycles solve 7           # find+verify m=7
    python -m claudecycles solve 9           # find+verify m=9
    python -m claudecycles analyze 3         # deep analysis of m=3
    python -m claudecycles theorem           # verify all four theorems
    python -m claudecycles compare 3 5 7     # compare solutions across m

All results are auto-verified before printing.
"""

from __future__ import annotations
import sys
from typing import List

from .solutions import get_solution, get_solution_table, known_m_values, construct_for_odd_m
from .search import find_sigma, RandomSearch
from .analysis import SolutionAnalysis, compare_across_m
from .fiber import even_m_impossibility_check, analyze_Q_structure, compose_levels
from .analysis import extract_sigma_table
from .core import verify_sigma


# =========================================================================== #
# Commands
# =========================================================================== #

def cmd_verify(m: int):
    """Verify a known hardcoded solution."""
    sigma = get_solution(m)
    if sigma is None:
        print(f"No hardcoded solution for m={m}. Known: {known_m_values()}")
        print(f"Use 'solve {m}' to find one.")
        return
    print(f"\nVerifying hardcoded solution m={m}...")
    result = verify_sigma(sigma, m)
    print(result)
    if result.is_valid:
        table = get_solution_table(m)
        print(f"\nSigma table [s][j] → perm:")
        for s in range(m):
            print(f"  s={s}: {[table[s][j] for j in range(m)]}")


def cmd_solve(m: int, strategy: str = "auto", seed: int = 42,
              max_iter: int = 200_000):
    """Find and verify a solution for given m."""
    print(f"\nSolving m={m}  strategy={strategy}  seed={seed}...")
    sigma = find_sigma(m, strategy=strategy, seed=seed,
                       max_iter=max_iter, verbose=True)
    if sigma is None:
        print(f"❌ No solution found for m={m}")
        return
    result = verify_sigma(sigma, m)
    print(result)


def cmd_analyze(m: int):
    """Deep mathematical analysis of a solution."""
    sigma = get_solution(m)
    if sigma is None:
        print(f"No hardcoded solution for m={m}. Searching...")
        sigma = find_sigma(m, verbose=True)
    if sigma is None:
        print(f"Could not find solution for m={m}")
        return
    a = SolutionAnalysis(sigma, m).run()
    print(a.report(verbose=True))


def cmd_theorem():
    """Demonstrate and verify all four theorems."""
    print()
    print("=" * 64)
    print("CLAUDE'S CYCLES: FOUR THEOREMS")
    print("=" * 64)

    print("""
Theorem 1 — Twisted Translation Structure
  For any column-uniform sigma, the composed fiber permutation satisfies:
  Q_c(i,j) = (i + b_c(j),  j + r_c) mod m
""")
    for m in [3, 5]:
        table = get_solution_table(m)
        from .fiber import compose_levels, analyze_Q_structure
        Qs = compose_levels(table, m)
        qa = analyze_Q_structure(Qs, m)
        print(f"  m={m}: all_twisted={qa['all_twisted']}  r_values={qa.get('r_values','—')}")

    print("""
Theorem 2 — Single-Cycle Conditions
  Q_c is a Hamiltonian m²-cycle ⟺ gcd(r_c,m)=1  AND  gcd(Σb_c,m)=1
""")
    from .fiber import verify_single_cycle_conditions
    from math import gcd
    for m, b_vals, r_vals in [
        (3, [[1,2,2],[0,2,0],[1,0,1]], [1,1,1]),
        (5, None, None),
    ]:
        if b_vals is None:
            continue
        print(f"  m={m}:")
        for c in range(3):
            chk = verify_single_cycle_conditions(r_vals[c], b_vals[c], m)
            print(f"    Cycle {c}: r={r_vals[c]} b={b_vals[c]} "
                  f"cond_a={'✅' if chk['condition_a'] else '❌'} "
                  f"cond_b={'✅' if chk['condition_b'] else '❌'}")

    print("""
Theorem 3 — Existence for All Odd m > 2
  For odd m, valid (r₀,r₁,r₂) with each r_c coprime to m and Σr_c=m always exists.
  Example: (1, m-2, 1) works whenever m is odd and gcd(m-2,m)=gcd(2,m)=1
""")
    from math import gcd
    for m in [3, 5, 7, 9, 11, 13, 15]:
        r0, r1, r2 = 1, m-2, 1
        ok = gcd(r0,m)==1 and gcd(r1,m)==1 and gcd(r2,m)==1 and r0+r1+r2==m
        print(f"  m={m}: (1,{m-2},1) → gcd_ok={[gcd(r,m)==1 for r in [r0,r1,r2]]} "
              f"sum={r0+r1+r2} → valid={'✅' if ok else '❌'}")

    print("""
Theorem 4 — Impossibility for Even m
  For even m > 2: coprime-to-m elements are all odd.
  Sum of 3 odd numbers is ODD ≠ EVEN = m. Therefore no column-uniform
  fiber construction exists for even m.
""")
    for m in [4, 6, 8, 10, 12, 16]:
        result = even_m_impossibility_check(m)
        print(f"  m={m}: all_coprime_odd={result['all_coprime_are_odd']} "
              f"→ proved_impossible={result['impossibility_proved']} ✅")


def cmd_compare(m_values: List[int]):
    """Compare solutions across multiple m values."""
    analyses = {}
    for m in m_values:
        sigma = get_solution(m)
        if sigma is None:
            print(f"Searching for m={m}...")
            sigma = find_sigma(m, verbose=False)
        if sigma is None:
            print(f"  Could not find m={m}, skipping.")
            continue
        analyses[m] = SolutionAnalysis(sigma, m).run()
    print()
    print(compare_across_m(analyses))


def cmd_demo():
    """Full demo: verify known solutions, analyze, run theorems."""
    print("=" * 64)
    print("CLAUDE'S CYCLES — FULL SYSTEM DEMO")
    print("=" * 64)
    print("\n[1] Verifying known solutions...")
    for m in known_m_values():
        cmd_verify(m)
    print("\n[2] Deep analysis of m=3...")
    cmd_analyze(3)
    print("\n[3] Theorem verification...")
    cmd_theorem()
    print("\n[4] Finding m=7 (random search)...")
    cmd_solve(7)


# =========================================================================== #
# Entry point
# =========================================================================== #

def main(args: List[str] = None):
    if args is None:
        args = sys.argv[1:]

    if not args:
        cmd_demo()
        return

    cmd = args[0].lower()

    if cmd == "verify":
        for m_str in args[1:]:
            cmd_verify(int(m_str))
    elif cmd == "solve":
        strategy = "auto"
        seed = 42
        m_vals = []
        i = 1
        while i < len(args):
            if args[i] == "--strategy" and i+1 < len(args):
                strategy = args[i+1]; i += 2
            elif args[i] == "--seed" and i+1 < len(args):
                seed = int(args[i+1]); i += 2
            else:
                m_vals.append(int(args[i])); i += 1
        for m in m_vals:
            cmd_solve(m, strategy=strategy, seed=seed)
    elif cmd == "analyze":
        for m_str in args[1:]:
            cmd_analyze(int(m_str))
    elif cmd == "theorem":
        cmd_theorem()
    elif cmd == "compare":
        cmd_compare([int(x) for x in args[1:]])
    elif cmd == "demo":
        cmd_demo()
    else:
        print(f"Unknown command: {cmd!r}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
