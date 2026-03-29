import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tgi_agent import TGIAgent
from tgi_core import TGICore
import numpy as np

def run_demo():
    print("═══════════════════════════════════════════════")
    print("  TGI SYSTEM DEMO — Phase 4: Topological Autonomy  ")
    print("═══════════════════════════════════════════════")

    agent = TGIAgent()

    # 1. Global Knowledge Overview
    print("\n[DEMO] Domain 1: Universal Knowledge Grid Status")
    print(agent.ontology_summary())

    # 2. Reasoning over Laws
    print("\n[DEMO] Domain 2: Reasoning over Ingested Laws")
    # Finding a concept
    print(f"Retrieving 'Closure_Lemma' coordinate...")
    coord = agent.core.ontology._find_coord("Closure_Lemma")
    print(f"  Result: {coord}")

    # 3. Natural Language (Hierarchical TLM Scale-up)
    print("\n[DEMO] Domain 3: Hierarchical TLM Generation (Scale-up)")
    response = agent.query("Topology is the study of", hierarchical=True)
    print(response)

    # 4. Symbolic Math (AIMO)
    print("\n[DEMO] Domain 4: Symbolic Reasoning (AIMO Engine)")
    response = agent.query("remainder when 3**5 is divided by 10")
    print(response)

    # 5. Autonomous K-Lift (Dynamic K-expansion)
    print("\n[DEMO] Domain 5: Dynamic K-Expansion (Autonomous Correction)")
    core = TGICore(4, 3)
    print(f"Reflecting on G_4^3: {core.reflect()}")
    print("Executing K-Lift: G_4^3 -> G_4^4")
    core.set_topology(4, 4)
    print(f"Reflecting on G_4^4: {core.reflect()}")

    # 6. Tensor-Fibration (Neural Weights)
    print("\n[DEMO] Domain 6: Tensor-Fibration Mapping (Neural Weights)")
    weights = np.random.randn(20, 20)
    print(agent.query(weights))

    # 7. Cross-Reasoning
    print("\n[DEMO] Domain 7: Multi-Manifold Cross-Reasoning")
    cross_res = agent.cross_reason([
        "x + 5 = 10",
        "101101",
        "The quick brown fox",
        [(0,0), (5,5)]
    ])
    print(cross_res)

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — Global Knowledge Verified")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
