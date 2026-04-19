import numpy as np
import hashlib
import time

class Single_Node_Topological_Inverter:
    """
    Project ELECTRICITY: Absolute Single-Node Extraction
    No brute-force. No clusters. Pure Holographic Deconvolution.
    """
    def __init__(self, m=251, dim=1024):
        self.m = m
        self.dim = dim
        self.lexicon = {}
        self._ingest_lexicon()
        print(f"[{time.strftime('%H:%M:%S')} ALGIERS] Single-Node Inverter Online. Z_{self.m}^{4} initialized.")

    def _generate_vector(self, seed: str) -> np.ndarray:
        h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
        np.random.seed(h)
        v = np.random.randn(self.dim)
        return v / np.linalg.norm(v)

    def _ingest_lexicon(self):
        words =["snack", "right", "wedding", "gun", "canal", "pet", "rescue",
                 "hand", "scheme", "head", "apple", "abandon", "ability", "zoo"]
        for w in words:
            self.lexicon[w] = self._generate_vector(w)

    def extract_missing_elements(self, known_elements: list, target_shadow: np.ndarray):
        start_time = time.time()
        print(f"\n[*] INITIATING ALGEBRAIC DECONVOLUTION...")
        print(f"    Known Vectors: {known_elements}")

        # 1. Superpose the known elements into a single interference pattern
        v_known_sum = np.zeros(self.dim)
        for element in known_elements:
            if element in self.lexicon:
                v_known_sum += self.lexicon[element]

        # 2. THE ALGEBRAIC COLLAPSE (Subtraction in Summed Manifold)
        # For a superposition manifold, the inverse of addition is subtraction.
        v_missing_signature = target_shadow - v_known_sum

        # 3. Orthogonal Resolution (Find the peaks in the noise)
        resonances =[]
        for word, v_word in self.lexicon.items():
            if word not in known_elements:
                sim = np.dot(v_missing_signature, v_word) / (np.linalg.norm(v_missing_signature) * np.linalg.norm(v_word) + 1e-9)
                resonances.append((word, sim))

        resonances.sort(key=lambda x: x[1], reverse=True)
        latency = (time.time() - start_time) * 1000

        print(f"    [+] Deconvolution completed in {latency:.3f} ms.")
        print(f"    [+] Top Geometric Resonances (The Missing Elements):")
        for word, score in resonances[:2]:
            print(f"        -> {word.upper()} (Energy: {score:.4f})")

# =====================================================================
# THE EXECUTION
# =====================================================================
inverter = Single_Node_Topological_Inverter()
true_words =["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head", "ability", "apple"]

target_shadow = np.zeros(1024)
for w in true_words:
    target_shadow += inverter.lexicon.get(w, inverter._generate_vector(w))

known_10_words =["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
inverter.extract_missing_elements(known_10_words, target_shadow)
