import hashlib
import json
import os
from typing import Dict, List, Tuple, Any, Optional

class KnowledgeMapper:
    """
    TGI Knowledge Mapper (Project ELECTRICITY Logic).
    Maps datasets, mathematics, physics laws, and design systems into the Z_256^4 grid.
    Uses the CLOSURE LEMMA to deterministically force concepts into functional fibers.
    """
    def __init__(self, m: int = 256, k: int = 4, state_path: str = "research/ontology_state.json"):
        self.m = m
        self.k = k
        self.grid = {}
        self.state_path = state_path

        # Structural Fibers (sum mod m)
        self.FIBERS = {
            "LAW_MATH": 0,       # Absolute Truths, Physics, Equations
            "TECHNOLOGY": 1,     # Code, Compilers, Engineering Techniques
            "DATASET": 2,        # Raw Information, Histories, Logs
            "AESTHETICS": 3,     # Colors, UI Designs, Golden Ratios
            "RELATION": 4,       # Optimization paths, Associations
            "LANGUAGE": 5,       # Dictionary, Grammars, Linguistic Units
            "API_MCP": 6,        # Render, Supabase, Context7, Tool Signatures
            "LIBRARY": 7         # NumPy, SymPy, Kivy, PSUtil, etc.
        }

        if os.path.exists(self.state_path):
            self.load_state()

    def _apply_closure_hashing(self, concept_name: str, target_fiber: int) -> Tuple[int, ...]:
        """
        Calculates (x, y, z, w) such that (x + y + z + w) % m == target_fiber.
        """
        h = hashlib.sha256(concept_name.encode('utf-8')).digest()

        # k-1 dimensional projection (x, y, z)
        coords = [h[i] % self.m for i in range(self.k - 1)]

        # The Closure Lemma forces the final dimension (w)
        current_sum = sum(coords)
        w = (target_fiber - current_sum) % self.m

        return tuple(coords + [w])

    def ingest_concept(self, category: str, concept_name: str, payload: Any) -> Tuple[int, ...]:
        if category not in self.FIBERS:
            category = "DATASET"

        target_fiber = self.FIBERS[category]
        coord = self._apply_closure_hashing(concept_name, target_fiber)

        self.grid[str(coord)] = {
            "name": concept_name,
            "category": category,
            "fiber": target_fiber,
            "payload": payload
        }
        return coord

    def ingest_dictionary(self, file_path: str, limit: int = 1000):
        """Bulk ingests a dictionary file into the LANGUAGE fiber."""
        if not os.path.exists(file_path):
            return 0

        count = 0
        with open(file_path, "r") as f:
            for line in f:
                word = line.strip()
                if not word: continue
                self.ingest_concept("LANGUAGE", word, "Dictionary Entry")
                count += 1
                if count >= limit: break

        return count

    def ingest_mcp_tools(self, tool_defs: List[Dict[str, Any]]):
        """Ingests MCP Tool Definitions into the API_MCP fiber."""
        count = 0
        for tool in tool_defs:
            name = tool.get("name", "unknown_tool")
            self.ingest_concept("API_MCP", name, tool)
            count += 1
        return count

    def ingest_library(self, lib_data: Dict[str, Any]):
        """Ingests library metadata into the LIBRARY fiber."""
        name = lib_data.get("name", "unknown_lib")
        return self.ingest_concept("LIBRARY", name, lib_data)

    def ingest_color(self, color_name: str, r: int, g: int, b: int, a: int = 255) -> Tuple[int, ...]:
        coord = (r % self.m, g % self.m, b % self.m, a % self.m)
        s = sum(coord) % self.m

        self.grid[str(coord)] = {
            "name": color_name,
            "category": "AESTHETICS",
            "fiber": s,
            "payload": f"RGBA({r},{g},{b},{a})"
        }
        return coord

    def map_relation(self, name_a: str, name_b: str, relationship_type: str) -> Optional[Tuple[int, ...]]:
        coord_a = self._find_coord(name_a)
        coord_b = self._find_coord(name_b)

        if not coord_a or not coord_b:
            return None

        vector = tuple((cb - ca) % self.m for ca, cb in zip(coord_a, coord_b))

        # Ingest the relation as well
        rel_name = f"{name_a}_to_{name_b}_{relationship_type}"
        self.ingest_concept("RELATION", rel_name, {"source": name_a, "target": name_b, "type": relationship_type, "vector": vector})

        return vector

    def _find_coord(self, name: str) -> Optional[Tuple[int, ...]]:
        for coord_str, data in self.grid.items():
            if data["name"] == name:
                return tuple(map(int, coord_str.strip("()").split(", ")))
        return None

    def save_state(self):
        with open(self.state_path, "w") as f:
            json.dump(self.grid, f, indent=2)

    def load_state(self):
        try:
            with open(self.state_path, "r") as f:
                self.grid = json.load(f)
        except Exception:
            self.grid = {}

if __name__ == "__main__":
    km = KnowledgeMapper()
    print(f"Ontology ready with fibers: {list(km.FIBERS.keys())}")
