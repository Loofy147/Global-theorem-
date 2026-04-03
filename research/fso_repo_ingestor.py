import os
import ast
import hashlib
import asyncio
from typing import Dict, Any, List, Tuple

class FSORepoPopulator:
    """
    Ingests entire codebases into the FSO manifold.
    Every function becomes a 'Logic Wave' reachable in O(1).
    """
    def __init__(self, m: int):
        self.m = m
        self.logic_inventory = {} # (x,y,z) -> Logic Metadata

    def get_coords(self, identifier: str) -> Tuple[int, int, int]:
        """Deterministically maps a function name to a Torus coordinate."""
        h = int(hashlib.sha256(identifier.encode()).hexdigest(), 16)
        return (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)

    def parse_repository(self, path: str):
        """Walks through the repo and extracts every function's logic."""
        # print(f"--- Ingesting: {path} ---")
        if os.path.isfile(path):
            self._extract_logic_from_file(path)
        else:
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(".py"):
                        full_path = os.path.join(root, file)
                        self._extract_logic_from_file(full_path)

    def _extract_logic_from_file(self, filepath: str):
        with open(filepath, "r") as f:
            try:
                tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Extract the actual code block
                        func_code = ast.unparse(node)
                        coords = self.get_coords(node.name)

                        # Store in the Holographic Layer (At Rest)
                        self.logic_inventory[coords] = {
                            "name": node.name,
                            "filepath": filepath,
                            "code": func_code,
                            "fiber": sum(coords) % self.m
                        }
            except Exception as e:
                pass # Skip files that can't be parsed

    def generate_logic_waves(self) -> List[Dict]:
        """Generates the 'Storage Wave' packets for the FSO Mesh."""
        packets = []
        for coords, meta in self.logic_inventory.items():
            packet = {
                "color": 0, # Storage/Logic Population Wave
                "target": coords,
                "type": "LOGIC_INJECT",
                "payload": {
                    "id": meta['name'],
                    "code": meta['code'],
                    "hash": hashlib.md5(meta['code'].encode()).hexdigest()
                }
            }
            packets.append(packet)
        return packets
