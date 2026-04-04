import os
import sys
import json
import hashlib
from typing import Tuple

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class JulesIngestor:
    def __init__(self, m=31):
        self.m = m
        self.manifest_path = "fso_production_manifest.json"
        self.state_path = "fso_manifold_state.json"

    def _get_coords(self, logic_id: str) -> Tuple[int, int, int]:
        h = int(hashlib.sha256(logic_id.encode()).hexdigest(), 16)
        return (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)

    def ingest(self):
        jules_logic = {
            "jules.plan_execute_verify": {
                "description": "Core Jules loop for autonomous task resolution.",
                "type": "agentic_behavior"
            },
            "jules.autopoietic_synthesis": {
                "description": "LLM-based logic synthesis for filling topological voids.",
                "type": "agentic_behavior"
            },
            "jules.tool_orchestration": {
                "description": "Optimal sequence determination for tool execution.",
                "type": "agentic_behavior"
            }
        }

        # Load Manifest
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r") as f:
                manifest = json.load(f)
        else:
            manifest = {}

        # Load State
        if os.path.exists(self.state_path):
            with open(self.state_path, "r") as f:
                state = json.load(f)
        else:
            state = {"registry": {}}

        for logic_id, info in jules_logic.items():
            coords = self._get_coords(logic_id)
            coord_str = str(coords)
            fiber = sum(coords) % self.m

            print(f"[*] Ingesting {logic_id} at {coord_str} (Fiber {fiber})")

            manifest[logic_id] = {
                "coords": list(coords),
                "fiber": fiber,
                "type": info["type"],
                "description": info["description"]
            }

            state["registry"][coord_str] = logic_id

        # Save updates
        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f, indent=4)

        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=4)

        print("[+] Jules logic successfully anchored in the manifold.")

if __name__ == "__main__":
    ingestor = JulesIngestor()
    ingestor.ingest()
