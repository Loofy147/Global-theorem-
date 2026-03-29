import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import List, Dict, Tuple, Any, Optional
import hashlib
from algebraic import AlgebraicClassifier
from core import solve, extract_weights

class TopologicalLanguageModel:
    """The Topological Language Model (TLM) with Path Lifting and Coordinate Mapping."""
    def __init__(self, m: int, k: int = 3):
        self.m = m
        self.k = k
        self.classifier = AlgebraicClassifier(m, k)
        from core import extract_weights
        self.weights = extract_weights(m, k)
        self._sigma = None # The discovered global structure

    def tokenize(self, text: str) -> List[int]:
        """Maps arbitrary text tokens to Z_m coordinates via hashing."""
        tokens = []
        # Simple word-based or char-based tokenizer
        words = text.split() if ' ' in text else list(text)
        for w in words:
            # Map word/char to an integer in [0, m-1]
            h = int(hashlib.md5(w.encode()).hexdigest(), 16)
            tokens.append(h % self.m)
        return tokens

    def _ensure_sigma(self):
        if self._sigma is None and not self.weights.h2_blocks:
            from core import solve
            self._sigma = solve(self.m, self.k)

    def topological_attention(self) -> float:
        """W4 Gauge Multiplicity acts as the 'attention breadth'."""
        return float(self.weights.h1_exact)

    def generate(self, seed_text: str, length: int) -> str:
        """Generates completion using Hamiltonian path lifting."""
        tokens = self.tokenize(seed_text)
        if self.weights.h2_blocks:
            return "[TOPOLOGICAL_ERROR: Obstruction detected]"

        self._ensure_sigma()
        if not self._sigma:
            return "[TOPOLOGICAL_ERROR: Failed to discover global structure]"

        current_tokens = list(tokens)

        # State vertex for the torus G_m^k
        state = [0]*self.k
        for i, t in enumerate(current_tokens[-self.k:]):
            state[self.k - min(len(current_tokens), self.k) + i] = t

        generated_tokens = []
        for _ in range(length):
            v = tuple(state)
            p = self._sigma.get(v)
            if not p: break

            # Follow Color 0's path
            arc_type = p[0]
            next_state = list(state)
            next_state[arc_type] = (next_state[arc_type] + 1) % self.m

            new_token = next_state[arc_type]
            generated_tokens.append(new_token)
            state = next_state

        # Mapping back to chars (simple lookup for this prototype)
        char_map = {i: chr(ord('a') + i % 26) for i in range(self.m)}
        return seed_text + " " + "".join(char_map[t] for t in generated_tokens)

if __name__ == "__main__":
    # TLM with m=3, k=3 (Solvable)
    tlm = TopologicalLanguageModel(m=3, k=3)
    print(f"TLM (m=3, k=3) Generation:")
    print(f"  Seed: 'hello world' -> {tlm.generate('hello world', 15)}")

    # TLM with m=7 (Odd)
    tlm_m7 = TopologicalLanguageModel(m=7, k=3)
    print(f"TLM (m=7, k=3) Generation:")
    print(f"  Seed: 'topology' -> {tlm_m7.generate('topology', 20)}")
