import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Tuple, Any, Optional
import hashlib
import numpy as np

class TGIParser:
    """The TGI-Parser: Maps datasets, languages, and math to topological parameters (m, k)."""

    def __init__(self):
        # Adjusted mappings: ensure solvable configurations (m odd or k even)
        self.router = {
            "math":       {"m": 9,   "k": 3, "core": "Symbolic"},  # Z_9^3 (odd m)
            "language":   {"m": 25,  "k": 3, "core": "TLM"},       # Z_25^3 (odd m)
            "binary":     {"m": 2,   "k": 4, "core": "Algebraic"},  # Z_2^4 (even k)
            "lattice":    {"m": 4,   "k": 4, "core": "Fibration"},  # Z_4^4 (even k)
            "heisenberg": {"m": 3,   "k": 3, "core": "Heisenberg"}, # Heisenberg H3(Z_3)
            "tsp":        {"m": 0,   "k": 0, "core": "Geometric"},   # TSP (Coordinate Manifolds)
            "knowledge":  {"m": 256, "k": 4, "core": "Ontology"},    # Z_256^4 (Ontology Grid)
            "neural":     {"m": 255, "k": 3, "core": "Neural"},    # Z_255^3 (odd m, solvable)
            "vision":     {"m": 255, "k": 5, "core": "Vision"},    # Z_256^5 (x,y,r,g,b)
            "default":    {"m": 3,   "k": 3, "core": "Basin"}
        }

    def parse_input(self, data: Any) -> Dict[str, Any]:
        """Detects content type and routes to the correct TGI core."""
        if isinstance(data, np.ndarray):
            if data.ndim == 3 and data.shape[-1] in [1, 3, 4]: # Likely Image
                return self._route("vision", data)
            return self._route("neural", data)
        elif isinstance(data, dict):
            if "category" in data and "name" in data:
                return self._route("knowledge", data)
            if "color" in data and "rgba" in data:
                return self._route("knowledge", data)
            if "points" in data:
                return self._route("lattice", data)
            if "weights" in data or "tensors" in data:
                return self._route("neural", data)
        elif isinstance(data, str):
            # Detection logic
            low_data = data.lower()
            if low_data.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                return self._route("vision", data)
            if "heisenberg" in low_data:
                return self._route("heisenberg", data)
            if any(c in data for c in "$=+-*/^"):
                return self._route("math", data)
            if all(c in "01 " for c in data) and len(data) > 0:
                return self._route("binary", data)
            return self._route("language", data)
        elif isinstance(data, list) and len(data) > 0 and (isinstance(data[0], tuple) or isinstance(data[0], list)):
            return self._route("tsp", data)
        return self._route("default", data)

    def _route(self, domain: str, raw_data: Any) -> Dict[str, Any]:
        params = self.router.get(domain, self.router["default"])
        return {
            "domain": domain,
            "m": params["m"],
            "k": params["k"],
            "target_core": params["core"],
            "payload": raw_data
        }

if __name__ == "__main__":
    parser = TGIParser()
    print("═══ TGI-PARSER UPDATED ROUTING ═══")
    test_inputs = [
        "x + 5 = 10",
        "Language",
        "image.png",
        np.zeros((64, 64, 3)),
        "1011",
        {"points": []},
        "Heisenberg Group",
        [(0.0, 0.0), (1.0, 1.0)],
        {"category": "LAW_MATH", "name": "Closure_Lemma", "payload": "Theory"},
        np.random.randn(10, 10)
    ]
    for inp in test_inputs:
        parsed = parser.parse_input(inp)
        print(f"Input: {str(inp)[:20]}... -> Domain: {parsed['domain']}, m={parsed['m']}, k={parsed['k']}, core={parsed['target_core']}")
