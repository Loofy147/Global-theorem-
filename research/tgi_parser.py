import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Tuple, Any, Optional
import hashlib

class TGIParser:
    """The TGI-Parser: Maps datasets, languages, and math to topological parameters (m, k)."""

    def __init__(self):
        # Adjusted mappings: ensure solvable configurations (m odd or k even)
        self.router = {
            "math":     {"m": 9,  "k": 3, "core": "Symbolic"}, # Z_9^3 (odd m)
            "language": {"m": 25, "k": 3, "core": "TLM"},      # Z_25^3 (odd m)
            "binary":   {"m": 2,  "k": 4, "core": "Algebraic"}, # Z_2^4 (even k)
            "lattice":  {"m": 4,  "k": 4, "core": "Fibration"}, # Z_4^4 (even k)
            "default":  {"m": 3,  "k": 3, "core": "Basin"}
        }

    def parse_input(self, data: Any) -> Dict[str, Any]:
        """Detects content type and routes to the correct TGI core."""
        if isinstance(data, str):
            # Detection logic
            if any(c in data for c in "$=+-*/^"):
                return self._route("math", data)
            if all(c in "01 " for c in data):
                return self._route("binary", data)
            return self._route("language", data)
        elif isinstance(data, dict) and "points" in data:
            return self._route("lattice", data)
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
    for inp in ["x + 5 = 10", "Language", "1011", {"points": []}]:
        parsed = parser.parse_input(inp)
        print(f"Domain: {parsed['domain']}, m={parsed['m']}, k={parsed['k']}")
