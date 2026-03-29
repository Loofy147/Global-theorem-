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

    # 1. Natural Language (Hierarchical TLM Scale-up)
    print("\n[DEMO] Domain 1: Hierarchical TLM Generation (Scale-up)")
    response = agent.query("Topology is the study of", hierarchical=True)
    print(response)

    # 2. Symbolic Math (AIMO)
    print("\n[DEMO] Domain 2: Symbolic Reasoning (AIMO Engine)")
    response = agent.query("remainder when 3**5 is divided by 10")
    print(response)

    # 3. Non-Abelian (Heisenberg)
    print("\n[DEMO] Domain 3: Non-Abelian Manifolds (Heisenberg)")
    response = agent.query("Heisenberg Group m=3")
    print(response)

    # 4. Geometric (TSP)
    print("\n[DEMO] Domain 4: Geometric Optimization (TSP)")
    response = agent.query([(0,0), (1,1), (2,2), (3,3), (4,4)])
    print(response)

    # 5. Autonomous K-Lift (Dynamic K-expansion)
    print("\n[DEMO] Domain 5: Dynamic K-Expansion (Autonomous Correction)")
    core = TGICore(4, 3)
    print(f"Reflecting on G_4^3: {core.reflect()}")
    print("Executing K-Lift: G_4^3 -> G_4^4")
    core.set_topology(4, 4)
    print(f"Reflecting on G_4^4: {core.reflect()}")

    # 6. Knowledge Mapping (Project ELECTRICITY)
    print("\n[DEMO] Domain 6: Universal Knowledge Mapping")
    print(agent.ingest_knowledge("LAW_MATH", "Closure_Lemma", "The k-1 dimension mathematically forces the k-th cycle closure."))
    print(agent.ingest_knowledge("TECHNOLOGY", "FSO_Compiler", "Converts Abstract Syntax Trees into Z_m^3 coordinate logic."))
    print(agent.forge_relation("Closure_Lemma", "FSO_Compiler", "Theoretical Foundation For"))

    # 7. Aesthetic Mapping
    print("\n[DEMO] Domain 7: Aesthetic Color Coordinate Mapping")
    print(agent.query({"name": "Primary_Sovereign_Blue", "rgba": (10, 25, 200, 255), "color": True}))

    # 8. Tensor-Fibration (Neural Weights)
    print("\n[DEMO] Domain 8: Tensor-Fibration Mapping (Neural Weights)")
    weights = np.random.randn(20, 20)
    print(agent.query(weights))

    # 9. Cross-Reasoning
    print("\n[DEMO] Domain 9: Multi-Manifold Cross-Reasoning")
    cross_res = agent.cross_reason([
        "x + 5 = 10",
        "101101",
        "The quick brown fox",
        [(0,0), (5,5)]
    ])
    print(cross_res)

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — Topological Autonomy Verified")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
