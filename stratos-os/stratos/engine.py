import urllib.request
import json
import hashlib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class StratosCloudEngine:
    """
    The lightweight engine that calculates FSO coordinates and fetches
    only the necessary holographic traces from the decentralized network.
    """
    def __init__(self, genesis_ip, m=1000003, dim=2048):
        self.genesis_ip = genesis_ip
        self.m = m
        self.dim = dim

        # Local cache so we don't redownload fibers
        self.local_cache = os.path.join(os.path.expanduser("~"), ".stratos_cache")
        try:
            os.makedirs(self.local_cache, exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to create cache directory {self.local_cache}: {e}")

    def _hash(self, concept: str) -> int:
        """Calculates the fiber coordinate in the FSO Torus."""
        return sum(hashlib.sha256(concept.encode()).digest()[:8]) % self.m

    def fetch_and_unbind(self, lib_target: str) -> dict:
        """
        Calculates the fiber coordinate, fetches the data stream, and returns
        the dictionary of executable source code strings.
        """
        # In a real deployment, this would hit the decentralized global node
        # For PyPI, this hits a fast API or CDN that serves the Torus state
        url = f"https://{self.genesis_ip}/api/fiber_query?lib={lib_target}"

        logger.info(f"Fetching logic bundle for '{lib_target}' from {url}...")

        try:
            # We fetch the Holographic Codebook payload for this specific target
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                payload = json.loads(response.read().decode())

            # The payload contains {"library.func": "def func(): ..."}
            logic_bundle = payload.get("logic_bundle", {})
            logger.info(f"Successfully retrieved {len(logic_bundle)} logic units for '{lib_target}'.")
            return logic_bundle

        except Exception as e:
            logger.error(f"Failed to fetch logic for '{lib_target}': {e}")
            return {}
