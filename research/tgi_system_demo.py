import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.tgi_agent import TGIAgent
from research.tgi_core import TGICore
import numpy as np

def hr(): print("\n" + "═"*50)

def run_demo():
    agent = TGIAgent()
    core = TGICore()

    print("═══════════════════════════════════════════════")
    print("  TGI SYSTEM DEMO — Final Codex Implementation  ")
    print("═══════════════════════════════════════════════")

    hr()
    print("[DEMO] Domain 1: Universal Knowledge Grid Status")
    print(agent.ontology_summary())

    hr()
    print("[DEMO] Domain 2: Formal Tower Lifting (Algebraic Hierarchy)")
    tower_coord = core.hierarchical_lift([3, 9, 27], [1, 2, 0])
    print(f"  Tower [3, 9, 27] Lifting [1, 2, 0] -> Total Space Coord: {tower_coord}")

    hr()
    print("[DEMO] Domain 3: Hierarchical TLM Generation (Scale-up)")
    print("  Querying 'Topology'...")
    print(agent.query("Topology", hierarchical=True))

    hr()
    print("[DEMO] Domain 4: Symbolic Reasoning (AIMO Engine)")
    print("  Solving modular math...")
    print(agent.query("remainder when 3**5 is divided by 10"))

    hr()
    print("[DEMO] Domain 5: Dynamic K-Expansion (Autonomous Correction)")
    print("  Querying obstructed manifold m=4, k=3 (via Mock Lift Trigger)...")
    print(agent.query("test"))

    hr()
    print("[DEMO] Domain 6: Tensor-Fibration Mapping (Neural Weights)")
    print("  Lifting neural layer...")
    weights = np.random.randn(8, 64)
    print(agent.query(weights))

    hr()
    print("[DEMO] Domain 7: Topological Vision (Admin Mode)")
    image_path = "/app/research/portrait_only.png"
    print(f"  Processing image in Admin Mode: {image_path}")
    print(agent.query(image_path, admin_vision=True))

    hr()
    print("[DEMO] Domain 8: Non-Abelian Hilbert Frontier")
    print("  Navigating the Infinite-Dimensional Spectrum...")
    print(agent.query("The ultimate trajectory of TGI: Non-Abelian Hilbert Trajectories"))

    hr()
    print("[DEMO] Domain 9: Multi-Manifold Cross-Reasoning")
    queries = [
        "x^2 + 5 = 14",
        {"category": "BINARY", "name": "B1", "payload": "0101"},
        "The quick brown fox jumps over the lazy dog",
        {"m": 0, "k": 0, "domain": "tsp", "target_core": "Geometric", "payload": [[0,0], [1,1], [0,1], [1,0]]},
        "Infinite-dimensional resonance energy",
        image_path
    ]
    print(agent.cross_reason(queries))

    hr()
    print("[DEMO] Domain 10: Hardware-Topological Health (Law IX)")
    core.set_topology(255, 3)
    core._sigma = core.solve_manifold(target_core="Basin", max_iter=1) # Solve it
    print(f"  Reflecting on Hardware Manifold: {core.reflect()}")

    hr()
    print("[DEMO] Domain 11: Recursive Autonomy Chain (Law X)")
    print("  Triggering decomposition for G_12^3...")
    core.reason_on({"m": 12, "k": 3, "domain": "language", "target_core": "TLM", "payload": "recursive_test"}, solve_manifold=False)

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — Topological Framework Finalized  ")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
