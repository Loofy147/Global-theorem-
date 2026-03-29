import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Optional, Tuple, Any
from algebraic import AlgebraicClassifier, GroupExtension, Tower
from core import solve, extract_weights, run_hybrid_sa, run_fiber_structured_sa
from tgi_parser import TGIParser
from research.aimo_reasoning_engine import AIMOReasoningEngine
from research.advanced_solvers import HeisenbergSolver, TSPSolver
from research.knowledge_mapper import KnowledgeMapper
from research.tensor_fibration import TensorFibrationMapper
from research.tgi_autonomy import SubgroupDiscovery, DynamicKLift
from research.topological_vision import TopologicalVisionMapper

class TGICore:
    """The heartbeat of Topological General Intelligence (TGI)."""
    def __init__(self, m: int = 3, k: int = 3):
        self.parser = TGIParser()
        self.math_engine = AIMOReasoningEngine()
        self.ontology = KnowledgeMapper(m=256, k=4)
        self.neural_mapper = TensorFibrationMapper(m=256, k=3)
        self.vision_mapper = TopologicalVisionMapper(m=256, k=5)
        self.set_topology(m, k)

    def set_topology(self, m: int, k: int):
        """Changes the current topological domain without wiping persistent engines."""
        self.m = m; self.k = k
        self.classifier = AlgebraicClassifier(m, k)
        from core import extract_weights
        if m > 0:
            self.weights = extract_weights(m, k)
            self.autonomy = SubgroupDiscovery(m, k)
            self.lift_engine = DynamicKLift(m, k)
        else:
            self.weights = None
            self.autonomy = None
            self.lift_engine = None
        self.status = self.classifier.analyze() if m > 0 else {"exists": "OPEN", "proof": ["1. Geometric manifold.", "2. Numerical search."]}
        self._sigma = None

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

    def reason_on(self, data: Any, solve_manifold: bool = True):
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

        if self.status.get("exists") == "PROVED_IMPOSSIBLE":
            new_k = self.lift_engine.suggest_lift() if self.lift_engine else None
            if new_k:
                print(f"  Autonomous Correction: {self.lift_engine.get_lift_reflection()}")
                self.set_topology(self.m, new_k)
                print(f"  New Status: {self.status.get('exists')}")
                print(f"  New Reflection: {self.reflect()}")

        if self.status.get("exists") != "PROVED_IMPOSSIBLE":
            if solve_manifold:
                sol = self.solve_manifold(target_core=parsed["target_core"], payload=parsed["payload"])
                if sol: print("  Global Manifold Completion: SUCCESS")
        else:
            print("  Topological Obstruction: NO SOLUTION REACHABLE")

    def reasoning_path(self) -> List[str]:
        return self.status.get("proof", ["1. Unknown domain.", "2. Brute-force search required."])

    def solve_manifold(self, max_iter: int = 5, target_core: str = "Basin", payload: Any = None) -> Optional[Any]:
        """Finds the global structure (Hamiltonian decomposition) with Basin Escape feedback."""
        if target_core == "Heisenberg":
            solver = HeisenbergSolver(self.m)
            sol, score = solver.solve(max_iter=max_iter)
            return sol

        if target_core == "Geometric" and payload:
            solver = TSPSolver("TGI_TSP", payload)
            tour, distance = solver.solve(max_iter=max_iter)
            return tour

        if target_core == "Ontology" and payload:
            if "category" in payload:
                return self.ontology.ingest_concept(payload["category"], payload["name"], payload["payload"])
            elif "rgba" in payload:
                return self.ontology.ingest_color(payload["name"], *payload["rgba"])

        if target_core == "Neural" and payload is not None:
            weights = payload["weights"] if isinstance(payload, dict) else payload
            return self.neural_mapper.lift_layer(weights)

        if target_core == "Vision" and payload is not None:
            return self.vision_mapper.lift_image(payload)

        if self.weights and self.weights.h2_blocks: return None
        if self._sigma is not None: return self._sigma

        self._sigma = solve(self.m, self.k, max_iter=max_iter)
        if self._sigma: return self._sigma

        if self.m > 0:
            if self.k == 3:
                sol, info = run_hybrid_sa(self.m, self.k, max_iter=max_iter)
            else:
                sol, info = run_fiber_structured_sa(self.m, self.k, max_iter=max_iter)
            self._sigma = sol

        return self._sigma

    def lift_path(self, sequence: List[int], color: int = 0) -> Optional[int]:
        sol = self.solve_manifold()
        if not sol or not isinstance(sol, dict): return None
        v = tuple(sequence[-self.k:] if len(sequence) >= self.k else [0]*(self.k-len(sequence)) + list(sequence))
        p = sol.get(v)
        if not p: return None
        arc_type = p[color]
        return (v[arc_type] + 1) % self.m

    def hierarchical_lift(self, orders: List[int], states: List[int]) -> int:
        """Formal tower lifting through multiple manifold layers."""
        tower = Tower(orders)
        return tower.lift_sequence(states)

    def measure_intelligence(self) -> float:
        return self.weights.compression if self.weights else 0.0

if __name__ == "__main__":
    tgi = TGICore()
    tgi.reason_on("x^2 + 5 = 14", solve_manifold=False)
