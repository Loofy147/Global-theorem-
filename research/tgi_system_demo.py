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

    # 2. Reasoning over Multi-Domain Laws
    print("\n[DEMO] Domain 2: Reasoning over Science & Physics Laws")
    for law in ["Second_Law_Thermodynamics", "Noether_Theorem", "Shannon_Entropy"]:
        coord = agent.core.ontology._find_coord(law)
        print(f"  Law: {law:<30} -> Coordinate: {coord}")

    # 3. Systems Architecture Mapping
    print("\n[DEMO] Domain 3: Systems Architecture & Computer Science")
    for tech in ["Turing_Completeness", "Blockchain_Consensus", "Kubernetes_Orchestration"]:
        coord = agent.core.ontology._find_coord(tech)
        print(f"  Tech: {tech:<30} -> Coordinate: {coord}")

    # 4. Cross-Domain Relation Check
    print("\n[DEMO] Domain 4: Cross-Domain Geometric Relations")
    rel_name = "General_Relativity_to_Topological_Language_Model_Manifold Curvature Analogy"
    vec = agent.core.ontology._find_coord(rel_name)
    print(f"  Rel: Relativity -> TLM (Curvature Analogy) -> Vector Node: {vec}")

    # 5. Natural Language (Hierarchical TLM Scale-up)
    print("\n[DEMO] Domain 5: Hierarchical TLM Generation (Scale-up)")
    response = agent.query("Topological General Intelligence is", hierarchical=True)
    print(response)

    # 6. Autonomous K-Lift (Dynamic K-expansion)
    print("\n[DEMO] Domain 6: Dynamic K-Expansion (Autonomous Correction)")
    core = TGICore(4, 3)
    print(f"Reflecting on G_4^3: {core.reflect()}")
    print("Executing K-Lift: G_4^3 -> G_4^4")
    core.set_topology(4, 4)
    print(f"Reflecting on G_4^4: {core.reflect()}")

    # 7. Tensor-Fibration (Neural Weights)
    print("\n[DEMO] Domain 7: Tensor-Fibration Mapping (Neural Weights)")
    weights = np.random.randn(20, 20)
    print(agent.query(weights))

    # 8. Cross-Reasoning
    print("\n[DEMO] Domain 8: Multi-Manifold Cross-Reasoning")
    cross_res = agent.cross_reason([
        "x + 5 = 10",
        "101101",
        "The quick brown fox",
        [(0,0), (5,5)]
    ])
    print(cross_res)

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — Enriched Knowledge Verified")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
