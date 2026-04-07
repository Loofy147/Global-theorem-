import numpy as np
import hashlib

class TopologicalLayer:
    """A single logical transformation layer in the TGI manifold."""
    def __init__(self, weight_vector, cleanup_gate=None):
        self.w = weight_vector
        self.cleanup = cleanup_gate

    def forward(self, x):
        # Y = W * X
        y = np.fft.ifft(np.fft.fft(self.w) * np.fft.fft(x)).real
        if self.cleanup:
            y, _ = self.cleanup.cleanup(y)
        return y

class TGICalculusEngine:
    """
    Implements the Topological Field Equations for TGI.
    Governs how logic flows, mutates, and learns in a 1024D manifold.
    """
    def __init__(self, dim=1024):
        self.dim = dim

    def generate_unitary(self, seed=None):
        if seed:
            state = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**32)
            np.random.seed(state)

        f_full = np.zeros(self.dim, dtype=complex)
        phases = np.random.uniform(0, 2*np.pi, self.dim // 2 - 1)
        f_full[0] = 1 if np.random.rand() > 0.5 else -1
        f_full[self.dim // 2] = 1 if np.random.rand() > 0.5 else -1
        f_full[1:self.dim // 2] = np.exp(1j * phases)
        f_full[self.dim // 2 + 1:] = np.conj(f_full[1:self.dim // 2][::-1])

        v = np.fft.ifft(f_full).real
        return v / np.linalg.norm(v)

    def bind(self, a, b):
        return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real

    def unbind(self, composite, a):
        """Holographic Retrieval: Circular Correlation (Exact inverse for unitary vectors)."""
        return np.fft.ifft(np.fft.fft(composite) * np.conj(np.fft.fft(a))).real

    def cosine_sim(self, v1, v2):
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 < 1e-9 or norm2 < 1e-9: return 0.0
        return np.dot(v1, v2) / (norm1 * norm2)

    def train_step(self, w_t, x, y_target, eta=1.0):
        y_pred = self.bind(w_t, x)
        error = y_pred - y_target
        gradient = self.unbind(error, x)
        w_next = w_t - eta * gradient
        return w_next, np.linalg.norm(error)
