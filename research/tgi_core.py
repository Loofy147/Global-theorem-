import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Optional, Tuple, Any
from algebraic import AlgebraicClassifier
from core import solve, extract_weights

class TGICore:
    """The heartbeat of Topological General Intelligence (TGI)."""
    def __init__(self, m: int, k: int):
        self.m = m; self.k = k
        self.classifier = AlgebraicClassifier(m, k)
        from core import extract_weights
        self.weights = extract_weights(m, k)
        self.status = self.classifier.analyze()
        self._sigma = None

    def reasoning_path(self) -> List[str]:
        """Returns the algebraic reasoning path for the current domain."""
        return self.status.get("proof", ["1. Unknown domain.", "2. Brute-force search required."])

    def solve_manifold(self) -> Optional[Dict]:
        """Finds the global structure (Hamiltonian decomposition) of the state space."""
        if self.weights.h2_blocks:
            return None # Impossible due to parity obstruction
        if self._sigma is None:
            self._sigma = solve(self.m, self.k)
        return self._sigma

    def lift_path(self, sequence: List[int], color: int = 0) -> Optional[int]:
        """Lifts a path (sequence) to its unique next point in the total space."""
        # Core B: Fibration Navigation
        sol = self.solve_manifold()
        if not sol: return None

        # Vertex representation in G_m^k
        v = tuple(sequence[-self.k:] if len(sequence) >= self.k else [0]*(self.k-len(sequence)) + list(sequence))
        p = sol.get(v)
        if not p: return None

        # Follow the arc for the given color
        arc_type = p[color]
        next_val = (v[arc_type] + 1) % self.m
        return next_val

    def measure_intelligence(self) -> float:
        """Calculates the Intelligence Quotient (IQ) as search compression W6."""
        # Lower compression ratio means higher 'intelligence' (better abstraction).
        return self.weights.compression

    def generate_report(self):
        print(f"╔═══════════════════════════════════════════════╗")
        print(f"║  TGI CORE — Topological General Intelligence   ║")
        print(f"╚═══════════════════════════════════════════════╝")
        print(f"  Domain: G_{self.m}^{self.k}")
        print(f"  Status: {self.status['exists']}")
        print(f"  IQ (W6 Compression): {self.measure_intelligence():.4f}")
        print(f"  Reasoning Path:")
        for step in self.reasoning_path():
            print(f"    {step}")

        sol = self.solve_manifold()
        if sol:
            print(f"  Global Structure: FOUND (Sigma verified)")
            # Demo a lift
            next_p = self.lift_path([0, 1, 2])
            print(f"  Path Lifting (Core B): [0, 1, 2] -> {next_p}")
        elif self.weights.h2_blocks:
            print(f"  Global Structure: OBSTRUCTED (H2 Parity Error)")
        else:
            print(f"  Global Structure: OPEN (Search in progress)")

if __name__ == "__main__":
    # Test on solvable (3,3) and obstructed (4,3)
    for (m, k) in [(3,3), (4,3)]:
        tgi = TGICore(m, k)
        tgi.generate_report()
        print()
