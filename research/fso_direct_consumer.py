import importlib
import subprocess
import sys
import hashlib
from typing import Any, Dict, Tuple

class FSODirectConsumer:
    """
    Directly consumes industrial-grade libraries (pip installed)
    and maps their functions to FSO Hamiltonian Coordinates.
    """
    def __init__(self, m: int):
        self.m = m
        self.call_cache = {}
        self.provisioned_packages = set()

    def _ensure_package(self, package_name: str):
        """Ensures the industry logic is present on the node."""
        if package_name in self.provisioned_packages: return
        try:
            importlib.import_module(package_name)
            self.provisioned_packages.add(package_name)
        except ImportError:
            print(f"[*] Node package '{package_name}' missing. Auto-provisioning logic...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                importlib.invalidate_caches()
                self.provisioned_packages.add(package_name)
            except Exception as e:
                print(f"[!] Failed to install {package_name}: {e}")

    def get_coords(self, function_identity: str) -> Tuple[int, int, int]:
        """Maps 'package.module.function' to a Torus coordinate."""
        h = int(hashlib.sha256(function_identity.encode()).hexdigest(), 16)
        return (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)

    def execute_logic(self, call_spec: str, params: Dict[str, Any]):
        """
        Example call_spec: 'skimage.filters.gaussian'
        The node imports it dynamically and executes it.
        """
        if call_spec in self.call_cache:
            func = self.call_cache[call_spec]
            try:
                p = params if params is not None else {}
                return func(**p) if callable(func) else func
            except Exception as e: return f"DIRECT_EXEC_ERROR: {str(e)}"

        parts = call_spec.split('.')
        package_name = parts[0]
        self._ensure_package(package_name)

        # Dynamic Resolution
        try:
            if len(parts) == 1:
                module = importlib.import_module(package_name)
                self.call_cache[call_spec] = module
                return module

            module_path = ".".join(parts[:-1])
            func_name = parts[-1]

            try:
                module = importlib.import_module(module_path)
            except ImportError:
                module = importlib.import_module(package_name)
                for part in parts[1:-1]:
                    module = getattr(module, part)

            func = getattr(module, func_name)
            self.call_cache[call_spec] = func

            if callable(func):
                p = params if params is not None else {}
                return func(**p)
            return func
        except Exception as e:
            return f"DIRECT_EXEC_ERROR: {str(e)}"
