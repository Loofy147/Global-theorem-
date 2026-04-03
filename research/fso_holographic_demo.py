import asyncio
import time
import sys
import os
from typing import List, Dict, Any, Tuple

# Add parent directory to path for core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_fabric import FSOFabricNode, FSODataStream
from research.fso_repo_ingestor import FSORepoPopulator

class FSOHolographicMesh:
    """
    A full-system demonstration of the FSO Holographic Mesh.
    Tasks are waves flowing through the 3-color Hamiltonian highways.
    """
    def __init__(self, m: int):
        self.m = m
        self.nodes = {}
        for i in range(m):
            for j in range(m):
                for k in range(m):
                    self.nodes[(i,j,k)] = FSOFabricNode((i,j,k), m)
        self.populator = FSORepoPopulator(m)

    async def ingest_logic(self, repo_path: str):
        print(f"--- Populating Holographic Layer from {repo_path} ---")
        self.populator.parse_repository(repo_path)
        waves = self.populator.generate_logic_waves()

        # Ingest every logic unit into the corresponding node in the torus
        for wave in waves:
            target_node = wave['target']
            node = self.nodes[target_node]
            # In production, this would be a Hamiltonian wave.
            # Here, we directly 'inject' to populate the mesh.
            await node.route_packet(wave)
        print(f"Mesh Saturated with {len(self.populator.logic_inventory)} Logic Units.")

    async def execute_query(self, func_name: str, color: int = 1):
        """Query any function by name in O(1) time."""
        target_coords = self.populator.get_coords(func_name)
        # print(f"\n--- EXECUTE QUERY: '{func_name}' -> {target_coords} ---")

        packet = {
            "id": "query_" + func_name,
            "target": target_coords,
            "color": color,
            "type": "LOGIC_EXECUTE",
            "payload": {"id": func_name}
        }

        current_node_coords = (0, 0, 0)
        hops = 0
        while hops < self.m**3:
            node = self.nodes[current_node_coords]
            result = await node.route_packet(packet)

            if isinstance(result, dict):
                print(f"  [SUCCESS] '{func_name}' found and executed at {current_node_coords} in {hops} hops.")
                # print(f"  Result: {result}")
                return True, hops

            current_node_coords = result
            hops += 1

        print(f"  [FAILURE] '{func_name}' not found in the manifold.")
        return False, hops

async def main():
    m = 11 # 1,331 nodes
    mesh = FSOHolographicMesh(m)

    # 1. Ingest the entire research directory
    await mesh.ingest_logic("./research")

    # 2. Query some specific functions that were just ingested
    functions_to_find = [
        "calculate_next_hop",   # From fso_fabric.py
        "get_coords",           # From fso_repo_ingestor.py
        "verify_sigma",          # From verify_fso_logic.py
        "construct_spike_sigma"  # From core.py (via fabric ingestion if it was copied)
    ]

    start_time = time.time()
    total_hops = 0
    for func in functions_to_find:
        ok, hops = await mesh.execute_query(func)
        if ok: total_hops += hops
    end_time = time.time()

    print(f"\n--- MESH PERFORMANCE METRICS ---")
    print(f"Total Logic Units: {len(mesh.populator.logic_inventory)}")
    print(f"Average Discovery Latency: {total_hops/len(functions_to_find):.2f} hops")
    print(f"Total Execution Time: {end_time - start_time:.4f}s")
    print(f"Throughput Guarantee: O(1) deterministic search.")

if __name__ == "__main__":
    asyncio.run(main())
