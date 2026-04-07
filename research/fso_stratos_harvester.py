import os
import sys
import subprocess
import importlib
import inspect
import numpy as np
import hashlib
from research.fso_saturation_core_v2 import StratosEngineV2

class StratosHarvester:
    """
    The Stratos Harvester: Deeply scans industrial libraries and binds their logic
    into the STRATOS OMEGA manifold.
    """
    def __init__(self, targets=None, dim=4096, memory_dir='./STRATOS_MEMORY_V2'):
        self.engine = StratosEngineV2(dim=dim, memory_dir=memory_dir)
        self.targets = targets or ["requests", "numpy", "json"]
        self.registry = {}

    def ensure_libraries(self):
        """Force install targets if they are missing."""
        print(f"[*] STRATOS: Synchronizing dependencies: {self.targets}")
        for lib in self.targets:
            try:
                importlib.import_module(lib)
            except ImportError:
                print(f"[!] {lib} missing. Injecting via pip...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

    def harvest_library(self, lib_name):
        """Deep scan a library for classes and functions to bind into the manifold."""
        print(f"[*] HARVESTING: {lib_name}...")
        try:
            module = importlib.import_module(lib_name)
        except Exception as e:
            print(f"[!] Failed to load {lib_name}: {e}")
            return

        count = 0
        # Recursive walk through the module members
        for name, obj in inspect.getmembers(module):
            # We target callable logic (Functions/Classes/Built-ins)
            if inspect.isfunction(obj) or inspect.isclass(obj) or inspect.isbuiltin(obj):
                full_path = f"{lib_name}.{name}"

                # Extract semantic signature (Source code or Bytecode)
                try:
                    # Attempt to get source; fallback to bytecode hash or representation
                    source = inspect.getsource(obj)
                except:
                    source = str(getattr(obj, "__code__", str(obj)))

                # Ingest into the HRR Manifold
                self.engine.ingest_semantic(full_path, obj)

                # Record the identity for the registry (using semantic signature)
                v_content = self.engine._generate_unitary_vector(source)
                self.registry[full_path] = v_content
                count += 1

        print(f"[+] Successfully bound {count} semantic traces for {lib_name}")

    def verify_manifold(self, query_path):
        """Test if the manifold can actually 'recall' the logic of a target."""
        print(f"[*] VERIFYING: {query_path}")
        retrieved_vec = self.engine.query(query_path)

        if retrieved_vec is None:
            print("[-] No trace found.")
            return

        # Compare against the registry of original 'content' vectors
        if query_path in self.registry:
            orig_vec = self.registry[query_path]

            # Normalization
            res_norm = retrieved_vec / (np.linalg.norm(retrieved_vec) + 1e-9)
            orig_norm = orig_vec / (np.linalg.norm(orig_vec) + 1e-9)

            similarity = np.dot(res_norm, orig_norm)
            print(f"[>] Retrieval Fidelity for {query_path}: {similarity:.4f}")
        else:
            print("[!] Query path not in local registry, cannot verify fidelity.")

if __name__ == "__main__":
    # Define our tactical targets
    tactical_targets = ["requests", "numpy", "json"]

    harvester = StratosHarvester(targets=tactical_targets, dim=2048)

    # 1. Prepare environment
    harvester.ensure_libraries()

    # 2. Ingest Targets
    for target in tactical_targets:
        harvester.harvest_library(target)

    # 3. Prove Retrieval
    harvester.verify_manifold("requests.get")
    harvester.verify_manifold("numpy.array")
    harvester.verify_manifold("json.dumps")
