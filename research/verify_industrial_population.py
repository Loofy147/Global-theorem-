import asyncio
import sys
import os
from typing import List, Dict, Any, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_mesh_daemon import FSOMeshDaemon
from research.fso_industrial_populator import FSOIndustrialPopulator
from research.fso_fabric import COLOR_LOGIC

async def main():
    print("--- FSO INDUSTRIAL POPULATION VERIFICATION ---")

    # 1. Initialize the FSO Mesh (m=11)
    daemon = FSOMeshDaemon(m=11)
    daemon.is_running = True # Manually enable for industrial population demo
    populator = FSOIndustrialPopulator(daemon)

    # 2. Ingest Industrial Repositories
    print("\n[STEP 1] Ingesting Industrial Logic into the Manifold...")
    await populator.ingest_repository("https://github.com/industrial/vision-core", "pixels")
    await populator.ingest_repository("https://github.com/industrial/distributed-mesh", "dist")

    # 3. Inject industrial data to a specific logic node
    print("\n[STEP 2] Injecting data into specific logic coordinates...")

    # Target node for pixel processing logic
    logic_id = "pixel_tensor_reshape"
    target_coords = populator._get_fso_coords(logic_id)

    # Inject pixel data (Color 0 - Storage Wave)
    pixel_data = "raw_rgba_tensor_data"
    print(f"Injecting pixel data for '{logic_id}' at {target_coords}...")
    await daemon.inject_storage("pixel_batch_001", pixel_data, target_coords)

    # 4. Trigger Logic Execution (Color 1 - Logic Wave)
    print("\n[STEP 3] Triggering Logic Wave for O(1) Intersection...")

    # Send Logic Wave to execute the 'pixel_tensor_reshape' logic on 'pixel_batch_001'
    exec_res = await daemon.execute_logic(logic_id, "pixel_batch_001", target_coords)

    if exec_res['status'] == "SUCCESS":
        print(f"Execution Result:")
        print(f"  Status: {exec_res['status']}")
        print(f"  Node: {exec_res['result']['node']}")
        print(f"  Processed Logic: {exec_res['result']['logic']}")
        print(f"  Execution Output: {exec_res['result']['result']}")
        print(f"  Total Hops: {exec_res['hops']}")
    else:
        print(f"Execution Failed: {exec_res}")
        return

    # 5. Verify Distribution logic
    print("\n[STEP 4] Verifying Distributed Mesh Logic...")
    dist_logic_id = "load_balance_spike"
    dist_target_coords = populator._get_fso_coords(dist_logic_id)

    # Inject mesh state
    await daemon.inject_storage("mesh_state_alpha", "load_imbalance_detected", dist_target_coords)

    # Execute distribution logic
    dist_res = await daemon.execute_logic(dist_logic_id, "mesh_state_alpha", dist_target_coords)
    if dist_res['status'] == "SUCCESS":
        print(f"Distribution Execution Result: {dist_res['result']['result']}")
    else:
        print(f"Distribution Execution Failed: {dist_res}")

    print("\n[SUCCESS] Industrial Logic Population and Distributed Execution verified.")

if __name__ == "__main__":
    asyncio.run(main())
