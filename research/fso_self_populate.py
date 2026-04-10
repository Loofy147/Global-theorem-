import os
import sys
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any

# Ensure we use the exact same logic as FSOTopology in apex_hypervisor
def get_fso_coords(logic_identity: str, m: int):
    h = int(hashlib.sha256(logic_identity.encode()).hexdigest(), 16)
    return (h % m, (h // m) % m, (h // (m**2)) % m)

class FSOSelfPopulator:
    def __init__(self, m: int):
        self.m = m
        self.manifest_path = "fso_production_manifest.json"
        self.state_path = "fso_manifold_state.json"
        self.manifest = {}
        self.registry = {}

        # Load existing manifest if present
        if os.path.exists(self.manifest_path):
            try:
                with open(self.manifest_path, "r") as f:
                    self.manifest = json.load(f)
            except:
                self.manifest = {}

        self.registry = {}

    def populate_all(self, engine=None):
        """Populates the manifold with batch ingestion support."""
        print(f"[*] Starting Global Self-Population (m={self.m})...")
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # Import refinery here to avoid path issues
        sys.path.insert(0, root_dir)
        from research.fso_refinery import FSORefinery
        refinery = FSORefinery(self.m)

        all_extracted_units = {} # logic_id -> code

        for root, dirs, files in os.walk(root_dir):
            if any(p in root for p in [".git", "__pycache__", "venv", "node_modules", "SOVEREIGN_MIND", "STRATOS_MEMORY_V2", "STRATOS_OMEGA_V2"]):
                continue

            for filename in files:
                if filename.endswith(".py"):
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, root_dir)
                    module_prefix = rel_path.replace(".py", "").replace("/", ".")

                    print(f"  [+] Smelting {rel_path}...")
                    units = refinery._smelt_file(filepath)

                    for unit in units:
                        # Full Logic Identity
                        logic_id = f"project.{module_prefix}.{unit['id']}"

                        # REDO COORDINATES HERE TO ENSURE PARITY
                        coords = get_fso_coords(logic_id, self.m)
                        coords_str = str(tuple(coords))

                        # Populate Manifest
                        self.manifest[logic_id] = {
                            "coords": coords,
                            "fiber": sum(coords) % self.m,
                            "type": unit['type'],
                            "origin": rel_path,
                            "code": unit['logic']
                        }

                        # Populate Registry
                        self.registry[coords_str] = logic_id
                        all_extracted_units[logic_id] = unit['logic']

        # If engine is provided, perform a batch ingestion for speed
        if engine and hasattr(engine, "batch_ingest_semantic"):
            print(f"[*] Batch Ingesting {len(all_extracted_units)} units into Stratos Manifold...")
            engine.batch_ingest_semantic(all_extracted_units)

    def save_results(self):
        # Save Manifest
        with open(self.manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=4)
        print(f"[!] Saved total {len(self.manifest)} units to {self.manifest_path}")

        # Save Manifold State (Full Sync)
        state_data = {
            "timestamp": datetime.now().isoformat(),
            "m_size": self.m,
            "registry": self.registry
        }
        with open(self.state_path, "w") as f:
            json.dump(state_data, f, indent=4)
        print(f"[!] Synchronized Manifold State: {len(self.registry)} active anchors in {self.state_path}")

if __name__ == "__main__":
    populator = FSOSelfPopulator(101)
    populator.populate_all()
    populator.save_results()
