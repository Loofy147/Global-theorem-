"""
claudecycles — Discovery system for Knuth's "Claude's Cycles" problem.

This system embodies the full reasoning and discovery process used to:
  1. Understand the digraph structure
  2. Discover the fiber decomposition
  3. Identify the twisted translation Q_c(i,j) = (i+b_c(j), j+r_c)
  4. Prove existence for odd m and impossibility for even m (column-uniform)
  5. Provide verified explicit solutions for m=3,5 and a constructive
     algorithm for any odd m

Public API
----------
  verify_sigma(sigma, m)            → VerifyResult
  find_sigma(m, strategy, ...)      → SigmaFn | None
  get_solution(m)                   → SigmaFn | None   (hardcoded m=3,5)
  construct_for_odd_m(m)            → SigmaFn | None
  SolutionAnalysis(sigma, m).run()  → deep analysis
  cli.main()                        → command-line interface

Quick start
-----------
  from claudecycles import get_solution, verify_sigma, SolutionAnalysis

  sigma = get_solution(3)
  result = verify_sigma(sigma, 3)
  print(result)                     # ✅ Valid 3-Hamiltonian decomposition

  analysis = SolutionAnalysis(sigma, 3).run()
  print(analysis.report())
"""

from .core import verify_sigma, VerifyResult, build_functional_graphs, trace_cycle, arc_sequence
from .fiber import compose_levels, analyze_Q_structure, even_m_impossibility_check
from .search import find_sigma, RandomSearch, BacktrackSearch, SimulatedAnnealing
from .analysis import SolutionAnalysis, compare_across_m
from .solutions import get_solution, get_solution_table, construct_for_odd_m, known_m_values

__all__ = [
    # Core
    "verify_sigma", "VerifyResult", "build_functional_graphs",
    "trace_cycle", "arc_sequence",
    # Fiber
    "compose_levels", "analyze_Q_structure", "even_m_impossibility_check",
    # Search
    "find_sigma", "RandomSearch", "BacktrackSearch", "SimulatedAnnealing",
    # Analysis
    "SolutionAnalysis", "compare_across_m",
    # Solutions
    "get_solution", "get_solution_table", "construct_for_odd_m", "known_m_values",
]

__version__ = "1.0.0"
