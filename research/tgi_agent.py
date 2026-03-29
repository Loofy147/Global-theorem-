import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Optional, Tuple, Any
from tgi_core import TGICore
from tlm import TopologicalLanguageModel
from tgi_parser import TGIParser

class TGIAgent:
    """The High-Level Topological General Intelligence (TGI) Agent."""
    def __init__(self):
        self.parser = TGIParser()
        self.core = TGICore()
        self.tlm = None # Initialized per query domain

    def query(self, data: Any):
        """Processes a query through the full TGI pipeline."""
        # 1. Parse and Route
        parsed = self.parser.parse_input(data)
        m, k = parsed["m"], parsed["k"]

        # 2. Update Core and TLM for the target manifold
        self.core.set_topology(m, k)
        if parsed["domain"] == "language":
            self.tlm = TopologicalLanguageModel(m, k)

        # 3. Generate Topological Reasoning Path
        print(f"╔═══════════════════════════════════════════════╗")
        print(f"║  TGI AGENT — {parsed['target_core']} Navigation ║")
        print(f"╚═══════════════════════════════════════════════╝")
        print(f"  Input: '{str(data)[:50]}...'")

        if parsed["domain"] == "math":
            ans = self.core.solve_math(data)
            return f"[TGI_RESPONSE: SYMBOLIC_SOLVE] Result: {ans}"

        print(f"  Moduli Space: M_{k}(G_{m})" if m > 0 else "  Moduli Space: Non-Abelian/Geometric")
        print(f"  Reasoning Path:")
        for step in self.core.reasoning_path():
            print(f"    {step}")

        # 4. Attempt Global Completion
        if self.core.status.get("exists") == "PROVED_IMPOSSIBLE":
            return f"[TGI_RESPONSE: TOPOLOGICAL_OBSTRUCTION] The query path is obstructed. "                    f"{self.core.reflect()}"

        # 5. Generate Response via Core/TLM
        if parsed["domain"] == "language":
            response = self.tlm.generate(data, 20)
            return f"[TGI_RESPONSE: LIFT_SUCCESS] {response}"

        elif parsed["domain"] == "heisenberg":
            sol = self.core.solve_manifold(target_core="Heisenberg")
            status = "SUCCESS" if sol else "FAILED"
            return f"[TGI_RESPONSE: HEISENBERG_DECOMPOSITION] Status: {status}"

        elif parsed["domain"] == "tsp":
            tour = self.core.solve_manifold(target_core="Geometric", payload=data)
            status = "SUCCESS" if tour else "FAILED"
            return f"[TGI_RESPONSE: GEOMETRIC_OPTIMIZATION] Tour Length: {len(tour) if tour else 0}, Status: {status}"

        return f"[TGI_RESPONSE: STRUCTURE_DISCOVERED] Manifold G_{m}^{k} solved with IQ {self.core.measure_intelligence():.4f}."

    def cross_reason(self, data_list: List[Any]) -> str:
        """Decomposes multiple queries and merges results for comparative reasoning."""
        results = []
        for data in data_list:
            parsed = self.parser.parse_input(data)
            self.core.set_topology(parsed["m"], parsed["k"])
            res = {
                "input": str(data)[:20],
                "domain": parsed["domain"],
                "m": parsed["m"],
                "k": parsed["k"],
                "exists": self.core.status.get("exists", "UNKNOWN"),
                "iq": self.core.measure_intelligence()
            }
            results.append(res)

        # Synthesized Reflection
        reflection = "═══ TGI CROSS-REASONING SYNTHESIS ═══\n"
        for r in results:
            reflection += f"- Domain {r['domain']} ({r['m']},{r['k']}): Status={r['exists']}, IQ={r['iq']:.4f}\n"

        # Comparison logic
        if any(r['exists'] == "PROVED_IMPOSSIBLE" for r in results) and any(r['exists'] == "PROVED_POSSIBLE" for r in results):
            reflection += "Conclusion: The input set contains both obstructed and solvable manifolds, indicating a topological phase transition."
        else:
            reflection += "Conclusion: The input set shows topological consistency across domains."

        return reflection

if __name__ == "__main__":
    agent = TGIAgent()

    # Test 1: Language
    print(agent.query("Topology is the study of"))
    print()

    # Test 2: Math
    print(agent.query("x + 5 = 14"))
    print()

    # Test 3: Heisenberg
    print(agent.query("Heisenberg Group m=3"))
    print()

    # Test 4: TSP
    print(agent.query([(0,0), (1,1), (2,0), (1,-1)]))
    print()

    # Test 5: Cross-Reasoning
    print(agent.cross_reason(["x+5=10", "10110", "Topology"]))
