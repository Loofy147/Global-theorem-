import asyncio
import json
import os
import sys
import time
from typing import Dict, Any, Tuple, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research.fso_fabric import FSOFabricNode, FSODataStream
from research.fso_repo_ingestor import FSORepoPopulator

class FSOMeshDaemon:
    """
    The Production Host for the FSO Geometric Supercomputer.
    Manages the 1,331-node Torus and serves distributed logic requests.
    """
    def __init__(self, m: int = 11):
        self.m = m
        self.nodes = {}
        for i in range(m):
            for j in range(m):
                for k in range(m):
                    self.nodes[(i,j,k)] = FSOFabricNode((i,j,k), m)
        self.populator = FSORepoPopulator(m)
        self.is_running = False

    async def bootstrap(self, paths: List[str]):
        """Populates the mesh with logic from specified paths."""
        print(f"--- FSO MESH DAEMON BOOTSTRAP (m={self.m}) ---")
        for path in paths:
            self.populator.parse_repository(path)

        waves = self.populator.generate_logic_waves()
        print(f"Injecting {len(waves)} logic units into the manifold...")

        for wave in waves:
            target_node = wave['target']
            await self.nodes[target_node].process_payload(wave)

        print(f"Manifold successfully populated. Total Logic Slots: {self.m**3}")
        self.is_running = True

    async def handle_request(self, request_type: str, logic_id: str, color: int = 1):
        """Dispatches an execution request into the Hamiltonian highway."""
        if not self.is_running:
            return {"status": "ERROR", "message": "Daemon not bootstrapped"}

        target_coords = self.populator.get_coords(logic_id)
        packet = {
            "id": f"req_{int(time.time())}",
            "target": target_coords,
            "color": color,
            "type": request_type, # e.g., LOGIC_EXECUTE
            "payload": {"id": logic_id}
        }

        # Hamiltonian Search
        current_node_coords = (0, 0, 0)
        hops = 0
        while hops < self.m**3:
            node = self.nodes[current_node_coords]
            result = await node.route_packet(packet)

            if isinstance(result, dict):
                return {
                    "status": "SUCCESS",
                    "logic": logic_id,
                    "result": result,
                    "hops": hops,
                    "target": target_coords
                }

            current_node_coords = result
            hops += 1

        return {"status": "FAILURE", "reason": "Logic not found in manifold", "hops": hops}

async def run_daemon():
    daemon = FSOMeshDaemon(m=11)
    # Self-host: Ingest our own production logic
    await daemon.bootstrap(["./research", "./core.py"])

    # Example queries to verify production readiness
    test_queries = ["calculate_next_hop", "construct_spike_sigma", "verify_sigma"]
    for query in test_queries:
        res = await daemon.handle_request("LOGIC_EXECUTE", query)
        print(f"Query '{query}': {res['status']} in {res['hops']} hops at {res['target']}")

if __name__ == "__main__":
    asyncio.run(run_daemon())
