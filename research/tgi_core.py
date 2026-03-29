import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Optional, Tuple, Any
from algebraic import AlgebraicClassifier
from core import solve, extract_weights
from tgi_parser import TGIParser

class TGICore:
    """The heartbeat of Topological General Intelligence (TGI)."""
    def __init__(self, m: int = 3, k: int = 3):
        self.m = m; self.k = k
        self.classifier = AlgebraicClassifier(m, k)
        from core import extract_weights
        self.weights = extract_weights(m, k)
        self.status = self.classifier.analyze()
        self._sigma = None
        self.parser = TGIParser()

    def set_topology(self, m: int, k: int):
        """Changes the current topological domain."""
        self.__init__(m, k)

    def reason_on(self, data: Any):
        """Routes and reasons over arbitrary data using the TGI-Parser."""
        parsed = self.parser.parse_input(data)
        self.set_topology(parsed["m"], parsed["k"])

        print(f"╔═══════════════════════════════════════════════╗")
        print(f"║  TGI REASONING — {parsed['target_core']} Core ║")
        print(f"╚═══════════════════════════════════════════════╝")
        print(f"  Input Type: {parsed['domain']}")
        print(f"  Topological IQ (W6): {self.measure_intelligence():.4f}")
        print(f"  Status: {self.status['exists']}")

        for step in self.reasoning_path():
            print(f"    {step}")

        if self.status["exists"] != "PROVED_IMPOSSIBLE":
            sol = self.solve_manifold()
            if sol: print("  Global Manifold Completion: SUCCESS")
        else:
            print("  Topological Obstruction: NO SOLUTION REACHABLE")

    def reasoning_path(self) -> List[str]:
        return self.status.get("proof", ["1. Unknown domain.", "2. Brute-force search required."])

    def solve_manifold(self) -> Optional[Dict]:
        if self.weights.h2_blocks: return None
        if self._sigma is None: self._sigma = solve(self.m, self.k)
        return self._sigma

    def lift_path(self, sequence: List[int], color: int = 0) -> Optional[int]:
        sol = self.solve_manifold()
        if not sol: return None
        v = tuple(sequence[-self.k:] if len(sequence) >= self.k else [0]*(self.k-len(sequence)) + list(sequence))
        p = sol.get(v)
        if not p: return None
        arc_type = p[color]
        return (v[arc_type] + 1) % self.m

    def measure_intelligence(self) -> float:
        return self.weights.compression

if __name__ == "__main__":
    tgi = TGICore()
    tgi.reason_on("x^2 + 5 = 14")
    print()
    tgi.reason_on("I love topology")
