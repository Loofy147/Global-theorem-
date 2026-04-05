import os
import sys
import json
import hashlib
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_refinery import FSORefinery

class FSOSelfPopulator:
    def __init__(self, m: int):
        self.m = m
        self.refinery = FSORefinery(m)
        self.manifest_path = "fso_production_manifest.json"
        self.manifest = {}
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r") as f:
                self.manifest = json.load(f)

    def populate_self(self):
        print(f"[*] Starting Self-Population (m={self.m})...")
        core_files = ["core.py", "algebraic.py", "fiber.py", "search.py", "solutions.py", "theorems.py"]
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        for filename in core_files:
            filepath = os.path.join(root_dir, filename)
            if not os.path.exists(filepath): continue
            print(f"  [+] Smelting {filename}...")
            units = self.refinery._smelt_file(filepath)
            module_name = filename.replace(".py", "")
            for unit in units:
                func_id = f"project.{module_name}.{unit['id']}"
                self.manifest[func_id] = {
                    "coords": unit['coords'],
                    "fiber": unit['fiber'],
                    "type": "project_logic"
                }
    def save_manifest(self):
        with open(self.manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=4)
        print(f"[!] Saved total {len(self.manifest)} units to {self.manifest_path}")

if __name__ == "__main__":
    populator = FSOSelfPopulator(31)
    populator.populate_self()
    populator.save_manifest()
