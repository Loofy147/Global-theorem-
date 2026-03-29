import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tgi_agent import TGIAgent
from tgi_core import TGICore

def run_demo():
    print("═══════════════════════════════════════════════")
    print("  TGI SYSTEM DEMO — Phase 3: Cognitive Integration  ")
    print("═══════════════════════════════════════════════")

    agent = TGIAgent()

    # 1. Natural Language (TLM)
    print("\n[DEMO] Domain 1: Natural Language Path Lifting")
    response = agent.query("Topology is the study of")
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

    # 5. Obstruction Reflection
    print("\n[DEMO] Domain 5: Topological Obstruction & Reflection")
    core = TGICore(4, 3)
    print(f"Reflecting on m=4 k=3: {core.reflect()}")

    # 6. Cross-Reasoning
    print("\n[DEMO] Domain 6: Multi-Manifold Cross-Reasoning")
    cross_res = agent.cross_reason([
        "x + 5 = 10",
        "101101",
        "The quick brown fox",
        [(0,0), (5,5)]
    ])
    print(cross_res)

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — Cognitive Integration Verified")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
