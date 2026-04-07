import numpy as np

class TopologicalCleanUpGate:
    """
    Stabilizes the Torus by snapping noisy vectors to the nearest clean unitary anchor.
    Essential for bypassing the HRR capacity limit (D / 2 ln D).
    """
    def __init__(self, dim=1024):
        self.dim = dim
        self.item_memory = [] # list of (vector, label)

    def register(self, vector, label):
        norm = np.linalg.norm(vector)
        clean_v = vector / norm if norm > 1e-9 else vector
        self.item_memory.append((clean_v, label))

    def cleanup(self, noisy_vector, threshold=0.2):
        if not self.item_memory:
            return noisy_vector, "NONE"

        norm = np.linalg.norm(noisy_vector)
        v_norm = noisy_vector / norm if norm > 1e-9 else noisy_vector

        best_sim = -1
        best_vec = None
        best_label = "UNKNOWN"

        for clean_v, label in self.item_memory:
            sim = np.dot(v_norm, clean_v)
            if sim > best_sim:
                best_sim = sim
                best_vec = clean_v
                best_label = label

        if best_sim >= threshold:
            return best_vec, best_label
        return noisy_vector, "NOISY"

if __name__ == "__main__":
    # Self-test
    dim = 1024
    gate = TopologicalCleanUpGate(dim=dim)

    # Generate clean vectors
    v1 = np.random.randn(dim)
    v1 /= np.linalg.norm(v1)
    gate.register(v1, "logic_gate_01")

    v2 = np.random.randn(dim)
    v2 /= np.linalg.norm(v2)
    gate.register(v2, "logic_gate_02")

    # Generate noisy version of v1
    noise = np.random.normal(0, 0.1, dim)
    noisy_v1 = v1 + noise

    cleaned, label = gate.cleanup(noisy_v1)
    print(f"Clean-up Result: {label}")
    sim_to_orig = np.dot(cleaned, v1)
    print(f"Fidelity to original: {sim_to_orig:.4f}")
