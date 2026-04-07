import numpy as np
from tgi_calculus_engine import TGICalculusEngine
from tgi_cleanup_gate import TopologicalCleanUpGate

def run_capacity_test():
    dim = 1024
    engine = TGICalculusEngine(dim=dim)
    gate = TopologicalCleanUpGate(dim=dim)

    # HRR Capacity Theory: C = D / 2lnD
    capacity_limit = int(dim / (2 * np.log(dim)))
    print(f"--- TGI CAPACITY BENCHMARK: DIM={dim} ---")
    print(f"Theoretical Capacity Limit (C): {capacity_limit}")

    # 1. Ingest items into a single global weight vector
    n_items = int(capacity_limit * 1.5) # Overwhelm the trace slightly
    print(f"Loading {n_items} items into a single continuous trace (w_global)...")

    keys = [engine.generate_unitary() for _ in range(n_items)]
    vals = [engine.generate_unitary() for _ in range(n_items)]

    # Initialize global weight as superposition of all mappings
    w_global = np.zeros(dim)
    for i in range(n_items):
        # Weight maps key -> val
        # W = sum(val_i # key_i) -- Wait, if Y = W * X, then W = Y # X
        mapping = engine.unbind(vals[i], keys[i])
        w_global += mapping
        gate.register(vals[i], f"val_{i}")

    # 2. Retrieval Benchmark (without Clean-up)
    print("\n--- RETRIEVAL WITHOUT CLEAN-UP ---")
    raw_cosines = []
    for i in range(20):
        # Y_pred = W * X_i
        y_pred = engine.bind(w_global, keys[i])
        raw_cosines.append(engine.cosine_sim(y_pred, vals[i]))

    avg_raw = np.mean(raw_cosines)
    print(f"Average Fidelity (Crosstalk): {avg_raw:.4f}")

    # 3. Retrieval Benchmark (with Clean-up Gate)
    print("\n--- RETRIEVAL WITH TOPOLOGICAL CLEAN-UP GATE ---")
    clean_cosines = []
    success_count = 0
    for i in range(20):
        y_pred = engine.bind(w_global, keys[i])
        # Use a lower threshold for high crosstalk
        y_clean, label = gate.cleanup(y_pred, threshold=0.1)

        sim_to_target = engine.cosine_sim(y_clean, vals[i])
        clean_cosines.append(sim_to_target)
        if label == f"val_{i}":
            success_count += 1

    avg_clean = np.mean(clean_cosines)
    print(f"Average Fidelity (Post-Cleanup): {avg_clean:.4f}")
    print(f"Logical Identity Recovery Rate: {success_count / 20 * 100:.1f}%")

    if success_count > 0:
        print(f"\n[SUCCESS] Clean-Up Gate recovered {success_count} logic units from {n_items} superimposed traces.")
    else:
        print("\n[STILL NOISY] Capacity limit too high or threshold too low.")

if __name__ == "__main__":
    run_capacity_test()
