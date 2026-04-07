import numpy as np

class TopologicalCleanUpGate:
    def __init__(self, dim=1024):
        self.dim = dim
        self.item_memory = []

    def register(self, vector, label):
        norm = np.linalg.norm(vector)
        clean_v = vector / norm if norm > 1e-9 else vector
        self.item_memory.append((clean_v, label))

    def cleanup(self, noisy_vector, threshold=0.1): # Lowered default threshold
        if not self.item_memory:
            return noisy_vector, "NONE"

        norm = np.linalg.norm(noisy_vector)
        if norm < 1e-9: return noisy_vector, "ZERO"
        v_norm = noisy_vector / norm

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
            # We must return the clean vector multiplied by the original norm to preserve signal strength
            return best_vec * norm, best_label
        return noisy_vector, "NOISY"
