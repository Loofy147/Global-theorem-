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
        self.tlm = TopologicalLanguageModel(m, k)

        # 3. Generate Topological Reasoning Path
        print(f"╔═══════════════════════════════════════════════╗")
        print(f"║  TGI AGENT — {parsed['target_core']} Navigation ║")
        print(f"╚═══════════════════════════════════════════════╝")
        print(f"  Input: '{str(data)[:50]}...'")
        print(f"  Moduli Space: M_{k}(G_{m})")
        print(f"  Reasoning Path:")
        for step in self.core.reasoning_path():
            print(f"    {step}")

        # 4. Attempt Global Completion
        if self.core.status["exists"] == "PROVED_IMPOSSIBLE":
            return f"[TGI_RESPONSE: TOPOLOGICAL_OBSTRUCTION] The query path is obstructed in Z_{m}^{k}. " \
                   f"The sum of generators parity contradicts the fiber group order."

        # 5. Generate Response via TLM Lifting
        if parsed["domain"] == "language":
            response = self.tlm.generate(data, 20)
            return f"[TGI_RESPONSE: LIFT_SUCCESS] {response}"

        elif parsed["domain"] == "math":
            # For math, we use the symbolic core's reasoning path
            return f"[TGI_RESPONSE: SYMBOLIC_PROOF] {self.core.reasoning_path()[-1]}"

        return f"[TGI_RESPONSE: STRUCTURE_DISCOVERED] Manifold G_{m}^{k} solved with IQ {self.core.measure_intelligence():.4f}."

if __name__ == "__main__":
    agent = TGIAgent()

    # Test 1: Language
    print(agent.query("Topology is the study of"))
    print()

    # Test 2: Math (Obstructed in Z_10^3, now in Z_9^3)
    print(agent.query("x + 5 = 14"))
    print()

    # Test 3: Binary (Obstructed if m=4 k=3, now in m=2 k=4)
    print(agent.query("1010101011"))
