import asyncio
import sys
import os
import time
from typing import List, Dict, Any, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_mesh_daemon import FSOMeshDaemon
from research.fso_industrial_populator import FSOIndustrialPopulator
from research.fso_fabric import COLOR_STORAGE, COLOR_LOGIC, COLOR_CONTROL, FSODataStream

async def main():
    print("--- FSO-MCP PRODUCTION SHOWCASE (m=11, 1331 Nodes) ---")

    # 1. Initialize the FSO-MCP Mesh (m=11)
    # This bootstrap populates the manifold with real repo logic (Color 0)
    daemon = FSOMeshDaemon(m=11)

    print("\n[STEP 1] Bootstrapping Manifold with Real Repository Logic...")
    # Bootstrap from ./research to ingest the entire codebase
    await daemon.bootstrap(["./research"])

    # 2. Ingest Industrial Varieties (Pixels, Dist, Text)
    print("\n[STEP 2] Anchoring Industrial Variety Specifications (Theorem 4.4)...")
    populator = FSOIndustrialPopulator(daemon)
    await populator.ingest_repository("https://github.com/industrial/vision-core", "pixels")
    await populator.ingest_repository("https://github.com/industrial/distributed-mesh", "dist")

    # 3. Activate Autopoietic Expansion
    print("\n[STEP 3] Triggering Autopoietic Expansion: 'Generative Logic' Synthesis...")

    # We ask the manifold for a dashboard script it doesn't have yet.
    # The node will hit its Generative Gate and anchor the new logic on-the-fly.
    target_node = (5, 5, 5) # Central coordinate
    task_id = "health_dashboard_v1"
    instruction = "a function that creates a system health dashboard string with nodes and load stats"
    system_stats = {"nodes": daemon.m**3, "load": 0.12}

    packet_gen = {
        "color": COLOR_LOGIC,
        "target": target_node,
        "payload": {
            "id": task_id,
            "instruction": instruction,
            "data": system_stats
        }
    }

    # Send the generative logic wave
    gen_res = await daemon.handle_request(packet_gen)

    print(f"Generative Synthesis Result:")
    print(f"  Status: {gen_res['status']}")
    print(f"  Logic Output: {gen_res['result']['result']}")
    print(f"  Hops to Authoring Gate: {gen_res['hops']}")

    # 4. Multimodal Logic Intersection (Theorem 4.2)
    print("\n[STEP 4] Executing Multimodal Hamiltonian Wave Sequence...")

    # Logic 1: Real Code (From Repo)
    repo_logic = "calculate_next_hop"
    repo_target = daemon.get_coords(repo_logic)
    res_repo = await daemon.execute_logic(repo_logic, None, repo_target)
    print(f"  [Repo Logic] '{repo_logic}' intersection at {repo_target} in {res_repo['hops']} hops.")

    # Logic 2: Industrial Spec (From Pixels)
    pixel_logic = "pixel_tensor_reshape"
    pixel_target = populator._get_fso_coords(pixel_logic)
    # Inject data first
    await daemon.inject_storage("pixel_frame_0", "rgba(255, 0, 0, 1)", pixel_target)
    # Execute intersection
    res_pixel = await daemon.execute_logic(pixel_logic, "pixel_frame_0", pixel_target)
    print(f"  [Industrial Spec] '{pixel_logic}' intersection at {pixel_target} in {res_pixel['hops']} hops.")
    print(f"  Result: {res_pixel['result']['result']}")

    # 5. Global Mesh Sync (Control Wave)
    print("\n[STEP 5] Deploying Global Sync Wave (Color 2 - Healing)...")
    control_packet = {
        "color": COLOR_CONTROL,
        "target": (0, 0, 0),
        "payload": {"status": "GLOBAL_SYNC", "expected_fiber": 0}
    }
    sync_res = await daemon.handle_request(control_packet)
    print(f"  [Control Wave] Sync status: {sync_res['result']['status']} at Node {sync_res['result']['node']}")

    print("\n--- SHOWCASE COMPLETE ---")
    print(f"FSO Manifold Saturated: {len(daemon.populator.logic_inventory)} Repo Units + {len(populator.logic_registry)} Industrial Specs.")
    print(f"System State: GENERATIVE BIOSPHERE ACTIVE (Phase 12).")

if __name__ == "__main__":
    asyncio.run(main())
