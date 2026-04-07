import numpy as np
from tgi_calculus_engine import TGICalculusEngine, TopologicalLayer
from tgi_cleanup_gate import TopologicalCleanUpGate

def run_deep_tgi_test():
    dim = 1024
    engine = TGICalculusEngine(dim=dim)
    gate = TopologicalCleanUpGate(dim=dim)

    print("--- TGI: DEEP TOPOLOGICAL LEARNING TEST (NOISY MANIFOLD) ---")

    # 1. Define Sequence
    x = engine.generate_unitary()
    h_target = engine.generate_unitary()
    y_target = engine.generate_unitary()

    gate.register(h_target, "HIDDEN")
    gate.register(y_target, "OUTPUT")

    # 2. Setup Weights
    w1_perfect = engine.unbind(h_target, x)
    w2_perfect = engine.unbind(y_target, h_target)

    # Add modest noise
    w1 = w1_perfect + np.random.normal(0, 0.05, dim)
    w2 = w2_perfect + np.random.normal(0, 0.05, dim)

    # 3. Execution with Clean-up
    print("[*] Inference WITH Clean-up Gate...")
    # Threshold needs to be high enough to match target but low enough to accept noise
    l1 = TopologicalLayer(w1, cleanup_gate=gate)
    l2 = TopologicalLayer(w2, cleanup_gate=gate)

    h_pred = l1.forward(x)
    y_pred = l2.forward(h_pred)
    sim_y = engine.cosine_sim(y_pred, y_target)
    print(f"    Final Fidelity: {sim_y:.4f}")

    # 4. Execution WITHOUT Clean-up
    print("[*] Inference WITHOUT Clean-up Gate...")
    l1_n = TopologicalLayer(w1, cleanup_gate=None)
    l2_n = TopologicalLayer(w2, cleanup_gate=None)

    h_n = l1_n.forward(x)
    y_n = l2_n.forward(h_n)
    sim_y_n = engine.cosine_sim(y_n, y_target)
    print(f"    Final Fidelity: {sim_y_n:.4f}")

    if sim_y > sim_y_n:
        print("\n[SUCCESS] Clean-up Gate prevents error propagation.")
    else:
        print(f"\n[DEBUG] sim_y: {sim_y:.4f}, sim_y_n: {sim_y_n:.4f}")

if __name__ == "__main__":
    run_deep_tgi_test()
