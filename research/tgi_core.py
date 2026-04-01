import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Optional, Tuple, Any
from algebraic import AlgebraicClassifier, GroupExtension, Tower
from core import solve, extract_weights, run_hybrid_sa, repair_manifold
from research.tgi_parser import TGIParser

class TGICore:
    """The heartbeat of Topological General Intelligence (TGI). Governing by the FSO Codex Laws I-XII."""
    def __init__(self, m: int = 3, k: int = 3):
        self.parser = TGIParser()
        try:
            from research.aimo_reasoning_engine import AIMOReasoningEngine
            self.math_engine = AIMOReasoningEngine()
        except ImportError:
            self.math_engine = None

        try:
            from research.knowledge_mapper import KnowledgeMapper
            self.ontology = KnowledgeMapper(m=256, k=4)
        except ImportError:
            self.ontology = None

        try:
            from research.tensor_fibration import TensorFibrationMapper
            self.neural_mapper = TensorFibrationMapper(m=256, k=3)
        except ImportError:
            self.neural_mapper = None

        try:
            from research.topological_vision import TopologicalVisionMapper
            self.vision_mapper = TopologicalVisionMapper(m=256, k=5)
        except ImportError:
            self.vision_mapper = None

        try:
            from research.hardware_awareness import HardwareMapper
            self.hardware = HardwareMapper(m=255, k=3)
        except ImportError:
            self.hardware = None

        self.set_topology(m, k)

    def set_topology(self, m: int, k: int):
        """Changes the current topological domain without wiping persistent engines."""
        self.m = m; self.k = k
        self.classifier = AlgebraicClassifier(m, k)
        from core import extract_weights
        if m > 0:
            self.weights = extract_weights(m, k)
            try:
                from research.tgi_autonomy import SubgroupDiscovery, DynamicKLift
                self.autonomy = SubgroupDiscovery(m, k)
                self.lift_engine = DynamicKLift(m, k)
            except ImportError:
                self.autonomy = None
                self.lift_engine = None
        else:
            self.weights = None
            self.autonomy = None
            self.lift_engine = None
        self.status = self.classifier.analyze() if m > 0 else {"exists": "OPEN", "proof": ["1. Geometric manifold.", "2. Numerical search."]}
        self._sigma = None

    def reflect(self) -> str:
        """Topological Reflection: Explains the current state manifold via FSO Laws."""
        if self.weights and self.weights.h2_blocks:
            return f"The manifold G_{self.m}^{self.k} is obstructed by an H2 parity class (Law I). Even grid + Odd dimensions is a fundamental topological limit."

        if self.m > 0 and self.k == 3 and self.m % 2 != 0:
            return f"The manifold G_{self.m}^3 is solvable via the Golden Path (Law IV). The Spike Construction deterministically generates Hamiltonian broadcast cycles."

        explanation = f"The manifold G_{self.m}^{self.k} is solvable (Law III/VI). " if self.m > 0 else "Advanced geometry detected (Law VI). "
        if self.weights:
            if self.weights.r_count > 0:
                explanation += f"It has {self.weights.r_count} valid fiber-stratified construction seeds (Law II). "
            explanation += f"The moduli space M is a torsor of order {self.weights.h1_exact} (Law III). "
            explanation += f"Abstraction IQ (W6) is {self.measure_intelligence():.4f} (Law XII). "
            if self.hardware:
                health = self.hardware.verify_hamiltonian_health(self._sigma)
                explanation += f"Physical Manifold (Law IX): {health}."
        else:
            explanation += "(Geometric/Non-Abelian/Continuous)."

        return explanation

    def solve_math(self, latex: str) -> int:
        """Symbolic-Topological solver governed by Law XI."""
        return self.math_engine.solve(latex) if self.math_engine else 0

    def reason_on(self, data: Any, solve_manifold: bool = True):
        """Routes and reasons over arbitrary data using the TGI-Parser and FSO Laws."""
        parsed = self.parser.parse_input(data)
        self.set_topology(parsed["m"], parsed["k"])

        print(f"╔═══════════════════════════════════════════════╗")
        print(f"║  TGI REASONING — {parsed['target_core']} Core ║")
        print(f"╚═══════════════════════════════════════════════╝")
        print(f"  Input Type: {parsed['domain']} (Law XI)")

        if parsed["domain"] == "math":
            ans = self.solve_math(data)
            print(f"  Symbolic Result: {ans}")
            return

        print(f"  Status: {self.status.get('exists', 'UNKNOWN')}")
        print(f"  Reflection: {self.reflect()}")

        if self.autonomy:
            decomp = self.autonomy.decompose_recursive()
            print(f"  Recursive Decomposition (Law X): {len(decomp)} steps discovered.")
            for step in decomp:
                print(f"    {step}")

        if "proof" in self.status:
            print("  Proof Chain:")
            for step in self.status["proof"]:
                print(f"    {step}")

        if self.status.get("exists") == "PROVED_IMPOSSIBLE":
            new_k = self.lift_engine.suggest_lift() if self.lift_engine else None
            if new_k:
                print(f"  Autonomous Correction (Law I): {self.lift_engine.get_lift_reflection()}")
                self.set_topology(self.m, new_k)
                print(f"  New Status: {self.status.get('exists')}")
                print(f"  New Reflection: {self.reflect()}")

        if self.status.get("exists") != "PROVED_IMPOSSIBLE":
            if solve_manifold:
                try:
                    sol = self.solve_manifold(target_core=parsed["target_core"], payload=parsed["payload"])
                    if sol: print("  Global Manifold Completion: SUCCESS (Law III)")
                except Exception as e:
                    print(f"  Solver Error: {e}")
        else:
            print("  Topological Obstruction (Law I/V): NO SOLUTION REACHABLE")

    def reasoning_path(self) -> List[str]:
        return self.status.get("proof", ["1. Unknown domain.", "2. Brute-force search required."])

    def solve_manifold(self, max_iter: int = 5, target_core: str = "Basin", payload: Any = None) -> Optional[Any]:
        """Finds the global structure (Hamiltonian decomposition) with Sovereign optimization."""
        if target_core == "Heisenberg":
            try:
                from research.advanced_solvers import HeisenbergSolver
                solver = HeisenbergSolver(self.m)
                sol, score = solver.solve(max_iter=max_iter)
                return sol
            except ImportError: return None

        if target_core == "Geometric" and payload:
            try:
                from research.advanced_solvers import TSPSolver
                solver = TSPSolver("TGI_TSP", payload)
                tour, distance = solver.solve(max_iter=max_iter)
                return tour
            except ImportError: return None

        if target_core == "Ontology" and payload:
            if self.ontology:
                if "category" in payload:
                    return self.ontology.ingest_concept(payload["category"], payload["name"], payload["payload"])
                elif "rgba" in payload:
                    return self.ontology.ingest_color(payload["name"], *payload["rgba"])
            return None

        if target_core == "Neural" and payload is not None:
            if self.neural_mapper:
                weights = payload["weights"] if isinstance(payload, dict) else payload
                return self.neural_mapper.lift_layer(weights)
            return None

        if target_core == "Vision" and payload is not None:
            return self.vision_mapper.lift_image(payload) if self.vision_mapper else None

        if self.weights and self.weights.h2_blocks: return None
        if self._sigma is not None: return self._sigma

        try:
            self._sigma = solve(self.m, self.k, max_iter=max_iter)
        except Exception as e:
            if "H^2 Parity Obstruction" in str(e):
                return None
            raise e

        if self._sigma: return self._sigma

        if self.m > 0:
            sol, info = run_hybrid_sa(self.m, self.k, max_iter=max_iter)
            if sol is None and info.get("best", 999) < 10:
                # Apply Law VII: Basin Escape Axiom
                print(f"  Attempting Basin Escape (Law VII) for score {info['best']}...")
                sol = repair_manifold(self.m, self.k, info["best_sigma"], max_iter=1000)
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
        """Formal tower lifting through multiple manifold layers (Law III)."""
        tower = Tower(orders)
        return tower.lift_sequence(states)

    def measure_intelligence(self) -> float:
        return self.weights.compression if self.weights else 0.0

if __name__ == "__main__":
    tgi = TGICore()
    tgi.reason_on("x^2 + 5 = 14", solve_manifold=False)
    tgi.reason_on({"category": "LAW_MATH", "name": "NonCanonical", "payload": "Obs"}, solve_manifold=True)
