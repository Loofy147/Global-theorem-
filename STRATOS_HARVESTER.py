import os
import sys
import subprocess
import importlib
import inspect
import numpy as np
from STRATOS_CORE_V2 import StratosEngineV2

class StratosHarvester:
    def __init__(self, targets=None):
        # Synchronized dimension at 4096
        self.engine = StratosEngineV2(dim=4096)
        self.targets = targets or ["requests", "numpy", "json"]
        self.registry = {}

    def ensure_libraries(self):
        print(f"[*] STRATOS: Synchronizing dependencies: {self.targets}")
        for lib in self.targets:
            try:
                importlib.import_module(lib)
            except ImportError:
                print(f"[!] {lib} missing. Injecting...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

    def harvest_library(self, lib_name):
        print(f"[*] HARVESTING: {lib_name}...")
        try:
            module = importlib.import_module(lib_name)
        except Exception as e:
            print(f"[!] Failed to load {lib_name}: {e}")
            return

        count = 0
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) or inspect.isclass(obj):
                full_path = f"{lib_name}.{name}"
                try:
                    source = inspect.getsource(obj)
                except:
                    source = str(getattr(obj, "__code__", "opaque_logic"))

                self.engine.ingest_semantic(full_path, obj)
                # Store expected vector for validation
                self.registry[full_path] = self.engine._generate_unitary_vector(source)
                count += 1
        print(f"[+] Successfully bound {count} traces for {lib_name}")

    def verify_manifold(self, query_path):
        print(f"[*] VERIFYING: {query_path}")
        retrieved_vec = self.engine.query(query_path)
        if retrieved_vec is None:
            print("[-] No trace found.")
            return

        if query_path in self.registry:
            orig_vec = self.registry[query_path]
            similarity = np.dot(retrieved_vec, orig_vec) / (np.linalg.norm(retrieved_vec) * np.linalg.norm(orig_vec))
            print(f"[>] Retrieval Fidelity for {query_path}: {similarity:.4f}")

if __name__ == "__main__":
    tactical_targets = ["requests", "numpy", "json"]
    harvester = StratosHarvester(targets=tactical_targets)
    harvester.ensure_libraries()
    for target in tactical_targets:
        harvester.harvest_library(target)

    harvester.verify_manifold("requests.get")
    harvester.verify_manifold("numpy.array")
