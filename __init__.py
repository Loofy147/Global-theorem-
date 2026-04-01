"""
claudecycles — Discovery system for Knuth's "Claude's Cycles" problem.
"""

from .core import verify_sigma, Weights, extract_weights
from .fiber import compose_levels, analyze_Q_structure, even_m_impossibility_check
from .search import find_sigma, SimulatedAnnealing
from .solutions import get_solution, get_solution_table, construct_for_odd_m, known_m_values

__all__ = [
    # Core
    "verify_sigma", "Weights", "extract_weights",
    # Fiber
    "compose_levels", "analyze_Q_structure", "even_m_impossibility_check",
    # Search
    "find_sigma", "SimulatedAnnealing",
    # Solutions
    "get_solution", "get_solution_table", "construct_for_odd_m", "known_m_values",
]

__version__ = "1.0.0"
