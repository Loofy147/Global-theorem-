import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Optional, Tuple, Any
from research.tgi_core import TGICore
from research.tlm import TopologicalLanguageModel
from research.tgi_parser import TGIParser
from research.hierarchical_tlm import HierarchicalTLM
from research.agentic_action_engine import TopologicalActionEngine
import numpy as np

class TGIAgent:
    """The High-Level Topological General Intelligence (TGI) Agent."""
    def __init__(self):
        self.parser = TGIParser()
        self.core = TGICore()
        self.tlm = None # Initialized per query domain
        self.htlm = None
        self.action_engine = TopologicalActionEngine()

    def query(self, data: Any, hierarchical: bool = False, admin_vision: bool = False):
        """Processes a query through the full TGI pipeline."""
        # 1. Parse and Route
        parsed = self.parser.parse_input(data)
        m_orig, k_orig = parsed["m"], parsed["k"]

        # 2. Update Core and TLM for the target manifold
        print(f"╔═══════════════════════════════════════════════╗")
        print(f"║  TGI AGENT — {parsed['target_core']} Navigation ║")
        print(f"╚═══════════════════════════════════════════════╝")
        print(f"  Input: '{str(data)[:50]}...'")

        if parsed["domain"] == "math":
            ans = self.core.solve_math(data)
            return f"[TGI_RESPONSE: SYMBOLIC_SOLVE] Result: {ans}"

        # 3. Handle reasoning and potential lifts
        self.core.reason_on(data, solve_manifold=False)
        m, k = self.core.m, self.core.k # Capture (potentially lifted) params

        if parsed["domain"] == "language":
            if hierarchical:
                self.htlm = HierarchicalTLM(m, k, depth=2)
            else:
                self.tlm = TopologicalLanguageModel(m, k)

        print(f"  Moduli Space: M_{k}(G_{m})" if m > 0 else "  Moduli Space: Non-Abelian/Geometric")
        print(f"  Reasoning Path:")
        for step in self.core.reasoning_path():
            print(f"    {step}")

        # 4. Attempt Global Completion
        if self.core.status.get("exists") == "PROVED_IMPOSSIBLE":
            return f"[TGI_RESPONSE: TOPOLOGICAL_OBSTRUCTION] The query path is obstructed. "                    f"{self.core.reflect()}"

        # 5. Generate Response via Core/TLM
        lifted = (m != m_orig or k != k_orig)
        lift_msg = f" (Manifold Lift: G_{m_orig}^{k_orig} -> G_{m}^{k})" if lifted else ""

        if parsed["domain"] == "language":
            if hierarchical and self.htlm:
                response = self.htlm.generate_hierarchical(data, 20)
                return f"[TGI_RESPONSE: HIERARCHICAL_LIFT_SUCCESS]{lift_msg} {response}"
            else:
                response = self.tlm.generate(data, 20)
                return f"[TGI_RESPONSE: LIFT_SUCCESS]{lift_msg} {response}"

        elif parsed["domain"] == "heisenberg":
            sol = self.core.solve_manifold(target_core="Heisenberg")
            status = "SUCCESS" if sol else "FAILED"
            return f"[TGI_RESPONSE: HEISENBERG_DECOMPOSITION]{lift_msg} Status: {status}"

        elif parsed["domain"] == "tsp":
            tour = self.core.solve_manifold(target_core="Geometric", payload=data)
            status = "SUCCESS" if tour else "FAILED"
            return f"[TGI_RESPONSE: GEOMETRIC_OPTIMIZATION]{lift_msg} Tour Length: {len(tour) if tour else 0}, Status: {status}"

        elif parsed["domain"] == "knowledge":
            coord = self.core.solve_manifold(target_core="Ontology", payload=data)
            return f"[TGI_RESPONSE: KNOWLEDGE_INGESTED]{lift_msg} Concept mapped to {coord}"

        elif parsed["domain"] == "neural":
            res = self.core.solve_manifold(target_core="Neural", payload=data)
            return f"[TGI_RESPONSE: NEURAL_LIFTED]{lift_msg} Topological Entropy: {res['topological_entropy']:.4f}, Points: {len(res['points'])}"

        elif parsed["domain"] == "vision":
            res = self.core.solve_manifold(target_core="Vision", payload=data)
            resp = f"[TGI_RESPONSE: VISION_LIFTED]{lift_msg} Entropy: {res['topological_entropy']:.4f}, Points: {res['points_count']}"
            if admin_vision:
                resp += f"\n[ADMIN_VISION] Signature: {res['topological_signature']}"
                resp += f"\n[ADMIN_VISION] Cohomological Gradient: {res['cohomological_gradient']:.4f}"
            return resp

        return f"[TGI_RESPONSE: STRUCTURE_DISCOVERED]{lift_msg} Manifold G_{m}^{k} solved with IQ {self.core.measure_intelligence():.4f}."

    def ingest_knowledge(self, category: str, name: str, payload: Any):
        return self.query({"category": category, "name": name, "payload": payload})

    def forge_relation(self, name_a: str, name_b: str, relation_type: str):
        vec = self.core.ontology.map_relation(name_a, name_b, relation_type)
        return f"[TGI_RESPONSE: RELATION_FORGED] {name_a} --({relation_type})--> {name_b} | Vector: {vec}"

    def ontology_summary(self) -> str:
        """Provides a summary of the Universal Ontology Mapper state."""
        grid = self.core.ontology.grid
        count = len(grid)
        cats = {}
        for d in grid.values():
            cats[d["category"]] = cats.get(d["category"], 0) + 1

        summary = f"═══ TGI ONTOLOGY SUMMARY ═══\n"
        summary += f"Total Entities: {count}\n"
        summary += f"Fiber Distribution:\n"
        for cat, c in cats.items():
            summary += f"  - {cat}: {c} entities\n"
        return summary

    def autonomous_query(self, intent: str) -> Dict[str, Any]:
        """Performs a multi-step autonomous topological plan generation."""
        # Detect target manifold (m=25, k=3 for language)
        parsed = self.parser.parse_input(intent)
        m, k = parsed["m"], parsed["k"]

        # Initialize TLM and generate path
        tlm = TopologicalLanguageModel(m, k)
        path = tlm.generate_path(intent, 20)

        # Resolve path to plan
        plan = self.action_engine.resolve_path_to_plan(path, intent)

        return {
            "intent": intent,
            "manifold": f"G_{m}^{k}",
            "path_length": len(path),
            "plan": plan
        }

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
    print(agent.ontology_summary())
