import os
import ast
import hashlib
import json
import logging
import sys
from typing import Dict, Any, List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CLAW_INGEST")

class ClawIngestor:
    def __init__(self, m: int = 31):
        self.m = m
        self.registry = {}
        self.state_file = "fso_manifold_state.json"

    def get_coords(self, identifier: str) -> Tuple[int, int, int]:
        h = int(hashlib.sha256(identifier.encode()).hexdigest(), 16)
        return (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)

    def ingest_repo(self, path: str):
        logger.info(f"[*] Starting ingestion of {path}")
        count = 0
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), path)
                    module_name = rel_path.replace("/", ".").replace(".py", "")
                    if module_name.endswith(".__init__"):
                        module_name = module_name[:-9]

                    self._process_file(os.path.join(root, file), module_name)
                    count += 1
        logger.info(f"[+] Processed {count} Python modules from claw-code.")

    def _process_file(self, filepath: str, module_prefix: str):
        try:
            with open(filepath, "r") as f:
                content = f.read()
                tree = ast.parse(content)

                # Ingest Functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        fid = f"claw.{module_prefix}.{node.name}"
                        coords = self.get_coords(fid)
                        # We store the reference to the file and line for the hypervisor to resolve
                        self.registry[str(coords)] = fid
                    elif isinstance(node, ast.ClassDef):
                        cid = f"claw.{module_prefix}.{node.name}"
                        coords = self.get_coords(cid)
                        self.registry[str(coords)] = cid
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")

    def update_manifold(self):
        logger.info("[*] Updating FSO Manifold State...")
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
        else:
            state = {"registry": {}}

        state["registry"].update(self.registry)
        state["last_ingestion"] = "claw-code"
        state["ingestion_timestamp"] = datetime.now().isoformat() if 'datetime' in globals() else time.time()

        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=4)
        logger.info(f"[+] Manifold updated with {len(self.registry)} claw-code units.")

if __name__ == "__main__":
    from datetime import datetime
    import time

    ingestor = ClawIngestor(m=31)
    ingestor.ingest_repo("temp_claw/src")
    ingestor.update_manifold()
