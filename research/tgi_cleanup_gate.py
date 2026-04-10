import numpy as np

class TopologicalCleanUpGate:
    def __init__(self, dim=1024):
        self.dim = dim
        self.item_memory = []
        self.vector_matrix = None

    def register(self, vector, label):
        norm = np.linalg.norm(vector)
        clean_v = vector / norm if norm > 1e-9 else vector
        self.item_memory.append((clean_v, label))
        self.vector_matrix = None

    def batch_register(self, vector_label_pairs):
        for vector, label in vector_label_pairs:
            norm = np.linalg.norm(vector)
            clean_v = vector / norm if norm > 1e-9 else vector
            self.item_memory.append((clean_v, label))
        self.vector_matrix = None

    def cleanup(self, noisy_vector, threshold=0.1): # Lowered default threshold
        if not self.item_memory:
            return noisy_vector, "NONE"

        if self.vector_matrix is None:
            self.vector_matrix = np.array([v for v, label in self.item_memory])

        norm = np.linalg.norm(noisy_vector)
        if norm < 1e-9: return noisy_vector, "ZERO"
        v_norm = noisy_vector / norm

        # Vectorized similarity: O(N*D) in BLAS
        sims = np.dot(self.vector_matrix, v_norm)
        best_idx = np.argmax(sims)
        best_sim = sims[best_idx]
        best_label = self.item_memory[best_idx][1]
        best_vec = self.item_memory[best_idx][0]

        if best_sim >= threshold:
            # We must return the clean vector multiplied by the original norm to preserve signal strength
            return best_vec * norm, best_label
        return noisy_vector, "NOISY"
