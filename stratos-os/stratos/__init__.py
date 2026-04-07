"""
STRATOS OS: Topological Import System
When a user imports this package, it automatically hooks into Python's core
and enables holographic library imports from the global Torus.
"""
import sys
import importlib.abc
import importlib.machinery
import types
import logging
from .engine import StratosCloudEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# 1. Initialize the Cloud Manifold connection
# It connects to your Genesis Node or a Cloud Storage bucket holding the .npy files
_MANIFOLD = StratosCloudEngine(genesis_ip="stratos-mainnet.fso.network")

class StratosPyPI_Importer(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """
    The ultimate sys.meta_path hijack.
    Allows: `import stratos.pandas` -> Fetches from the Torus instead of pip.
    """
    def find_spec(self, fullname, path, target=None):
        if fullname == "stratos" or fullname.startswith("stratos."):
            spec = importlib.machinery.ModuleSpec(fullname, self)
            spec.submodule_search_locations = [] # Make it a package
            return spec
        return None

    def create_module(self, spec):
        return types.ModuleType(spec.name)

    def exec_module(self, module):
        module.__package__ = module.__name__
        if module.__name__ == "stratos":
            # If it's the root 'stratos' package, we don't need to fetch logic yet
            return

        # 1. Parse the requested library (e.g., 'pandas')
        lib_target = module.__name__.split("stratos.")[1]
        logger.info(f"[⚡] STRATOS NATIVE IMPORT: Reconstituting '{lib_target}' from Torus...")

        # 2. Dynamically fetch the bundle of logic for this library
        logic_bundle = _MANIFOLD.fetch_and_unbind(lib_target)

        if not logic_bundle:
            logger.error(f"[!] Stratos Topological Void: '{lib_target}' not found in Manifold.")
            raise ImportError(f"Stratos Topological Void: '{lib_target}' not found in Manifold.")

        success_count = 0
        # 3. Compile the possible entities instantly into RAM
        for identity, source_code in logic_bundle.items():
            try:
                exec(source_code, module.__dict__)
                success_count += 1
            except Exception as e:
                logger.debug(f"Failed to execute logic unit '{identity}': {e}")

        logger.info(f"[+] Reconstituted {success_count} execution gates into '{module.__name__}'.")

# 2. Inject the hook into the Python Interpreter if not already present
if not any(isinstance(finder, StratosPyPI_Importer) for finder in sys.meta_path):
    sys.meta_path.insert(0, StratosPyPI_Importer())
