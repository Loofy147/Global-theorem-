import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tgi_agent import TGIAgent
from tgi_core import TGICore
import numpy as np

def run_demo():
    print("═══════════════════════════════════════════════")
    print("  TGI SYSTEM DEMO — Full Implementation Finalized  ")
    print("═══════════════════════════════════════════════")

    agent = TGIAgent()

    # 1. Global Knowledge Overview
    print("\n[DEMO] Domain 1: Universal Knowledge Grid Status")
    print(agent.ontology_summary())

    # 2. Formal Tower Lifting (Core B Hierarchy)
    print("\n[DEMO] Domain 2: Formal Tower Lifting (Algebraic Hierarchy)")
    core = agent.core
    tower_orders = [3, 9, 27]
    fiber_states = [1, 2, 0] # fibers at Level 0, 1, 2
    total_state = core.hierarchical_lift(tower_orders, fiber_states)
    print(f"  Tower {tower_orders} Lifting {fiber_states} -> Total Space Coord: {total_state}")

    # 3. Hierarchical TLM Generation (Scale-up)
    print("\n[DEMO] Domain 3: Hierarchical TLM Generation (Scale-up)")
    print("  Querying 'Topology'...")
    response = agent.query("Topology", hierarchical=True)
    print(response)

    # 4. Symbolic Math (AIMO Engine)
    print("\n[DEMO] Domain 4: Symbolic Reasoning (AIMO Engine)")
    print("  Solving modular math...")
    response = agent.query("remainder when 3**5 is divided by 10")
    print(response)

    # 5. Autonomous K-Lift (Dynamic K-expansion)
    print("\n[DEMO] Domain 5: Dynamic K-Expansion (Autonomous Correction)")
    print("  Querying obstructed manifold m=4, k=3 (via Mock Lift Trigger)...")
    class MockParser:
        def parse_input(self, data):
            return {"m": 4, "k": 3, "domain": "test", "target_core": "Basin", "payload": data}
    original_parser = agent.parser
    agent.parser = MockParser()
    agent.core.parser = MockParser()
    res = agent.query("test")
    print(res)
    agent.parser = original_parser
    agent.core.parser = original_parser

    # 6. Tensor-Fibration (Neural Weights)
    print("\n[DEMO] Domain 6: Tensor-Fibration Mapping (Neural Weights)")
    print("  Lifting neural layer...")
    weights = np.random.randn(5, 5) # Smaller weights
    print(agent.query(weights))

    # 7. Vision Core (Topological Computer Vision)
    print("\n[DEMO] Domain 7: Topological Vision (Admin Mode)")
    # Use the provided image if it exists
    image_path = os.path.join(os.path.dirname(__file__), "portrait_only.png")
    if os.path.exists(image_path):
        print(f"  Processing image in Admin Mode: {image_path}")
        print(agent.query(image_path, admin_vision=True))
    else:
        print("  Image not found, using synthetic fallback.")
        img = np.zeros((8, 8, 3), dtype=np.uint8)
        img[2:6, 2:6] = [255, 0, 0]
        print(agent.query(img, admin_vision=True))

    # 8. Cross-Reasoning
    print("\n[DEMO] Domain 8: Multi-Manifold Cross-Reasoning")
    dummy_img = np.zeros((4, 4, 3), dtype=np.uint8)
    cross_res = agent.cross_reason([
        "x + 5 = 10",
        "101101",
        "The quick brown fox",
        [(0,0), (1,1)],
        dummy_img
    ])
    print(cross_res)

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — Topological Framework Stable  ")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
