import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Optional, Tuple, Any
from algebraic import AlgebraicClassifier
from core import solve, extract_weights, run_hybrid_sa, run_fiber_structured_sa
from tgi_parser import TGIParser
from research.aimo_reasoning_engine import AIMOReasoningEngine
from research.advanced_solvers import HeisenbergSolver, TSPSolver

class TGICore:
    """The heartbeat of Topological General Intelligence (TGI)."""
    def __init__(self, m: int = 3, k: int = 3):
        self.m = m; self.k = k
        self.classifier = AlgebraicClassifier(m, k)
        from core import extract_weights
        if m > 0:
            self.weights = extract_weights(m, k)
        else:
            self.weights = None
        self.status = self.classifier.analyze() if m > 0 else {"exists": "OPEN", "proof": ["1. Geometric manifold.", "2. Numerical search."]}
        self._sigma = None
        self.parser = TGIParser()
        self.math_engine = AIMOReasoningEngine()

    def set_topology(self, m: int, k: int):
        """Changes the current topological domain."""
        self.__init__(m, k)

    def reflect(self) -> str:
        """Topological Reflection: Explains the current state manifold in natural language."""
        if self.weights and self.weights.h2_blocks:
            return f"The manifold G_{self.m}^{self.k} is obstructed. An H2 parity mismatch prevents a "                    f"Hamiltonian decomposition. This is a fundamental topological limit."

        explanation = f"The manifold G_{self.m}^{self.k} is solvable. " if self.m > 0 else "Advanced geometry detected. "
        if self.weights:
            if self.weights.r_count > 0:
                explanation += f"It has {self.weights.r_count} valid column-uniform construction seeds. "
            explanation += f"The moduli space M is a torsor of order {self.weights.h1_exact} (phi({self.m})). "
            explanation += f"Abstraction IQ (W6) is {self.measure_intelligence():.4f}."
        else:
            explanation += "(Geometric/Non-Abelian/Continuous)."

        return explanation

    def solve_math(self, latex: str) -> int:
        return self.math_engine.solve(latex)

    def reason_on(self, data: Any):
        """Routes and reasons over arbitrary data using the TGI-Parser."""
        parsed = self.parser.parse_input(data)
        self.set_topology(parsed["m"], parsed["k"])

        print(f"╔═══════════════════════════════════════════════╗")
        print(f"║  TGI REASONING — {parsed['target_core']} Core ║")
        print(f"╚═══════════════════════════════════════════════╝")
        print(f"  Input Type: {parsed['domain']}")

        if parsed["domain"] == "math":
            ans = self.solve_math(data)
            print(f"  Symbolic Result: {ans}")
            return

        print(f"  Status: {self.status.get('exists', 'UNKNOWN')}")
        print(f"  Reflection: {self.reflect()}")

        if self.status.get("exists") != "PROVED_IMPOSSIBLE":
            sol = self.solve_manifold(target_core=parsed["target_core"], payload=parsed["payload"])
            if sol: print("  Global Manifold Completion: SUCCESS")
        else:
            print("  Topological Obstruction: NO SOLUTION REACHABLE")

    def reasoning_path(self) -> List[str]:
        return self.status.get("proof", ["1. Unknown domain.", "2. Brute-force search required."])

    def solve_manifold(self, max_iter: int = 1000, target_core: str = "Basin", payload: Any = None) -> Optional[Any]:
        """Finds the global structure (Hamiltonian decomposition) with Basin Escape feedback."""
        if target_core == "Heisenberg":
            print(f"  Core H: Heisenberg Solver activated for m={self.m}")
            solver = HeisenbergSolver(self.m)
            sol, score = solver.solve(max_iter=max_iter)
            return sol

        if target_core == "Geometric" and payload:
            print(f"  Core G: Geometric (TSP) Solver activated for {len(payload)} cities")
            solver = TSPSolver("TGI_TSP", payload)
            tour, distance = solver.solve(max_iter=max_iter)
            return tour

        if self.weights and self.weights.h2_blocks: return None
        if self._sigma is not None: return self._sigma

        # Core C: Basin Escape Feedback Loop
        if self.m > 0:
            self._sigma = solve(self.m, self.k)
            if self._sigma: return self._sigma

            print(f"  Core C: Basin Escape activated for G_{self.m}^{self.k}")
            if self.k == 3:
                sol, info = run_hybrid_sa(self.m, self.k, max_iter=max_iter)
            else:
                sol, info = run_fiber_structured_sa(self.m, self.k, max_iter=max_iter)

            if sol:
                self._sigma = sol
                print(f"  Basin Escape successful: best_score={info['best']}, iters={info['iters']}")

        return self._sigma

    def lift_path(self, sequence: List[int], color: int = 0) -> Optional[int]:
        sol = self.solve_manifold()
        if not sol or not isinstance(sol, dict): return None
        v = tuple(sequence[-self.k:] if len(sequence) >= self.k else [0]*(self.k-len(sequence)) + list(sequence))
        p = sol.get(v)
        if not p: return None
        arc_type = p[color]
        return (v[arc_type] + 1) % self.m

    def measure_intelligence(self) -> float:
        return self.weights.compression if self.weights else 0.0

if __name__ == "__main__":
    tgi = TGICore()
    tgi.reason_on("x^2 + 5 = 14")
    print()
    tgi.set_topology(4, 3)
    print(f"Reflecting on m=4 k=3: {tgi.reflect()}")
