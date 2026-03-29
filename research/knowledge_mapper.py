import hashlib
import json
from typing import Dict, List, Tuple, Any, Optional

class KnowledgeMapper:
    """
    TGI Knowledge Mapper (Project ELECTRICITY Logic).
    Maps datasets, mathematics, physics laws, and design systems into the Z_256^4 grid.
    Uses the CLOSURE LEMMA to deterministically force concepts into functional fibers.
    """
    def __init__(self, m: int = 256, k: int = 4):
        self.m = m
        self.k = k
        self.grid = {}

        # Structural Fibers (sum mod m)
        self.FIBERS = {
            "LAW_MATH": 0,       # Absolute Truths, Physics, Equations
            "TECHNOLOGY": 1,     # Code, Compilers, Engineering Techniques
            "DATASET": 2,        # Raw Information, Histories, Logs
            "AESTHETICS": 3,     # Colors, UI Designs, Golden Ratios
            "RELATION": 4        # Optimization paths, Associations
        }

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

        self.grid[coord] = {
            "name": concept_name,
            "category": category,
            "fiber": target_fiber,
            "payload": payload
        }
        return coord

    def ingest_color(self, color_name: str, r: int, g: int, b: int, a: int = 255) -> Tuple[int, ...]:
        coord = (r % self.m, g % self.m, b % self.m, a % self.m)
        s = sum(coord) % self.m

        self.grid[coord] = {
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
        return vector

    def _find_coord(self, name: str) -> Optional[Tuple[int, ...]]:
        for coord, data in self.grid.items():
            if data["name"] == name:
                return coord
        return None

if __name__ == "__main__":
    km = KnowledgeMapper()
    c1 = km.ingest_concept("LAW_MATH", "Closure_Lemma", "Theory")
    c2 = km.ingest_concept("TECHNOLOGY", "FSO_Compiler", "Implementation")
    rel = km.map_relation("Closure_Lemma", "FSO_Compiler", "Foundational")
    print(f"Closure_Lemma: {c1}, FSO_Compiler: {c2}, Relation Vector: {rel}")
