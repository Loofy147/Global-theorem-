import asyncio
import json
import os
import sys
import time
import random
from typing import Dict, Any, Tuple, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research.fso_fabric import FSOFabricNode, FSODataStream, COLOR_STORAGE, COLOR_LOGIC, COLOR_CONTROL
from research.fso_repo_ingestor import FSORepoPopulator

class FSOMeshDaemon:
    """
    The Production Host for the FSO Geometric Supercomputer.
    Manages Tri-Color concurrent waves and distributed logic intersections.
    """
    def __init__(self, m: int = 11):
        self.m = m
        self.nodes = {}
        for i in range(m):
            for j in range(m):
                for k in range(m):
                    node = FSOFabricNode((i,j,k), m)
                    node.mesh_nodes = self.nodes
                    self.nodes[(i,j,k)] = node
        self.populator = FSORepoPopulator(m)
        self.is_running = False

    async def bootstrap(self, paths: List[str]):
        """Populates the mesh with logic from specified paths (Color 0)."""
        print(f"--- FSO MESH DAEMON BOOTSTRAP (m={self.m}) ---")
        for path in paths:
            self.populator.parse_repository(path)

        waves = self.populator.generate_logic_waves()
        print(f"Injecting {len(waves)} logic units into the manifold...")

        for wave in waves:
            target_node = wave['target']
            await self.nodes[target_node].route_packet(wave)

        print(f"Manifold successfully populated. Total Logic Slots: {self.m**3}")
        self.is_running = True

    async def handle_request(self, packet: Dict[str, Any]):
        """Dispatches a wave into the Hamiltonian highway."""
        if not self.is_running:
            return {"status": "ERROR", "message": "Daemon not bootstrapped"}

        current_node_coords = (0, 0, 0)
        hops = 0
        while hops < self.m**3:
            node = self.nodes[current_node_coords]
            result = await node.route_packet(packet)

            if isinstance(result, dict) and result.get("status") in ["EXECUTED", "STORED", "INGESTED", "VERIFIED", "HEALED", "LOGIC_READY"]:
                return {
                    "status": "SUCCESS",
                    "result": result,
                    "hops": hops
                }

            if result is None or isinstance(result, dict):
                # We hit the target but got no successful process status (e.g. NO_INTERSECTION)
                return {
                    "status": "FAILURE",
                    "result": result,
                    "hops": hops
                }

            current_node_coords = result
            hops += 1

        return {"status": "FAILURE", "reason": "No intersection found", "hops": hops}

    def get_coords(self, identifier: str) -> Tuple[int, int, int]:
        return self.populator.get_coords(identifier)

    async def inject_storage(self, key: str, data: Any, target: Tuple[int, int, int]):
        packet = FSODataStream.create_packet({"key": key, "data": data}, target, color=COLOR_STORAGE)
        return await self.handle_request(packet)

    async def execute_logic(self, logic_id: str, target_key: str, target_coords: Tuple[int, int, int]):
        packet = FSODataStream.create_packet({"id": logic_id, "target_key": target_key}, target_coords, color=COLOR_LOGIC)
        return await self.handle_request(packet)

async def run_daemon():
    daemon = FSOMeshDaemon(m=5)
    # Populate with actual fso_fabric logic
    await daemon.bootstrap(["./research/fso_fabric.py"])

    # 1. Inject data into Storage Wave (Color 0)
    # Target node for 'calculate_next_hop' logic
    target_coords = daemon.get_coords("calculate_next_hop")
    print(f"Target node for 'calculate_next_hop': {target_coords}")

    # Actually, bootstrap already injected the logic.
    # Let's verify it exists first.
    print("Verifying logic exists...")
    res_logic = await daemon.execute_logic("calculate_next_hop", None, target_coords)
    print(f"Logic Status: {res_logic}")

    print("Injecting sample data...")
    await daemon.inject_storage("doc_1", "Secret Logic Content", target_coords)

    # 2. Trigger Logic Intersection (Color 1)
    print("Triggering Logic Query...")
    res = await daemon.execute_logic("calculate_next_hop", "doc_1", target_coords)
    print(f"Result: {res}")

if __name__ == "__main__":
    asyncio.run(run_daemon())
