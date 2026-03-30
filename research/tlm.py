import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import List, Dict, Tuple, Any, Optional
import hashlib
from algebraic import AlgebraicClassifier
from core import solve, extract_weights
from research.knowledge_mapper import KnowledgeMapper

class TopologicalLanguageModel:
    """The Topological Language Model (TLM) with Path Lifting and Coordinate Mapping."""
    def __init__(self, m: int, k: int = 3):
        self.m = m
        self.k = k
        self.classifier = AlgebraicClassifier(m, k)
        # Handle weights based on available modules
        try:
            from core import extract_weights
            self.weights = extract_weights(m, k)
        except (ImportError, ModuleNotFoundError):
            self.weights = None

        self._sigma = None # The discovered global structure
        self.ontology = KnowledgeMapper()

    def tokenize(self, text: str) -> List[int]:
        """Maps arbitrary text tokens to Z_m coordinates via hashing."""
        tokens = []
        words = text.split() if ' ' in text else list(text)
        for w in words:
            # Map word/char to an integer in [0, m-1]
            h = int(hashlib.md5(w.encode()).hexdigest(), 16)
            tokens.append(h % self.m)
        return tokens

    def _ensure_sigma(self):
        if self._sigma is None and self.weights and not self.weights.h2_blocks:
            try:
                from core import solve
                self._sigma = solve(self.m, self.k)
            except (ImportError, ModuleNotFoundError):
                self._sigma = None

    def generate(self, seed_text: str, length: int) -> str:
        """Generates completion using Hamiltonian path lifting."""
        path = self.generate_path(seed_text, length)
        if not path:
            return self.generate_ontology_grounded(seed_text, length)

        generated_tokens = [c[0] for c in path] # Simple token extract for demo
        char_map = {i: chr(ord('a') + i % 26) for i in range(self.m)}
        return seed_text + " " + "".join(char_map[t] for t in generated_tokens)

    def generate_path(self, seed_text: str, length: int) -> List[Tuple[int, ...]]:
        """Lifts a seed into a Hamiltonian path of coordinates."""
        tokens = self.tokenize(seed_text)
        if self.weights and self.weights.h2_blocks:
            return []

        self._ensure_sigma()
        if not self._sigma:
            return []

        current_tokens = list(tokens)

        # State vertex for the torus G_m^k
        state = [0]*self.k
        for i, t in enumerate(current_tokens[-self.k:]):
            state[self.k - min(len(current_tokens), self.k) + i] = t

        path = []
        for _ in range(length):
            v = tuple(state)
            p = self._sigma.get(v)
            if not p: break

            arc_type = p[0]
            next_state = list(state)
            next_state[arc_type] = (next_state[arc_type] + 1) % self.m

            path.append(tuple(next_state))
            state = next_state

        return path

    def generate_ontology_grounded(self, seed_text: str, length: int) -> str:
        """Uses the LANGUAGE fiber in the Ontology to ground generation."""
        # Find concepts in the LANGUAGE fiber (index 5)
        words = []
        for coord_str, data in self.ontology.grid.items():
            if data["category"] == "LANGUAGE":
                words.append(data["name"])

        if not words:
            return seed_text + "... [ONTOLOGY_EMPTY]"

        # Select words based on simple hash of seed
        h = int(hashlib.md5(seed_text.encode()).hexdigest(), 16)
        res = [words[(h + i) % len(words)] for i in range(length // 5)]
        return seed_text + " " + " ".join(res)

if __name__ == "__main__":
    tlm = TopologicalLanguageModel(m=25, k=3)
    print(f"TLM (m=25, k=3) Generation:")
    print(f"  Seed: 'TGI' -> {tlm.generate('TGI', 10)}")
    print(f"  Path: {tlm.generate_path('TGI', 5)}")
