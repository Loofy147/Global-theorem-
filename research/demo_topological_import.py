import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_fabric import FSOFabricNode, COLOR_LOGIC, FSODataStream

async def run_demo():
    print("═══════════════════════════════════════════════")
    print("  FSO TOPOLOGICAL SELF-IMPORT DEMONSTRATION  ")
    print("═══════════════════════════════════════════════")

    m_val = 31

    # 1. Load the Manifest
    manifest_path = "research/fso_production_manifest.json"
    if not os.path.exists(manifest_path):
        print("[!] Manifest missing. Running self-populator...")
        os.system("python3 research/fso_self_populate.py")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # 2. Setup a target node for a "Self-Importing" function
    # Let's create a custom logic block that uses the topological_call helper
    target_id = "project.demo.self_importer"
    target_coords = (1, 2, 3) # Arbitrary fixed coord for the demo

    # This logic calls 'project.core.verify_sigma' via the manifold
    self_import_logic = """
async def self_importer(data):
    print(f"[SelfImporter] Received data: {data}")
    # TOPOLOGICAL IMPORT: Request logic from another coordinate
    result = await topological_call("project.core.verify_sigma", {"sigma": {}})
    return f"COMPLEX_PROCESS_COMPLETE: {result}"
"""

    node = FSOFabricNode(target_coords, m_val)

    # Manually anchor the logic into this node for the demo
    node.logic_registry[target_id] = {
        "id": target_id,
        "code": self_import_logic,
        "type": "project_logic"
    }

    # 3. Trigger the Logic Wave
    print(f"\n[*] Triggering Logic Wave for '{target_id}' at {target_coords}...")

    packet = FSODataStream.create_packet(
        {"id": target_id, "data": "Test_Data_123"},
        target_coords,
        color=COLOR_LOGIC
    )

    res = await node.route_packet(packet)

    print("\n[RESULT]:")
    print(json.dumps(res, indent=4))

    if res.get("status") == "EXECUTED" and "TOPOLOGICAL_RESULT_OF_project.core.verify_sigma" in res.get("result", ""):
        print("\n[SUCCESS] Topological Self-Import Verified!")
        print("The FSO node successfully resolved and 'imported' logic from itself.")
    else:
        print("\n[FAILURE] Self-import mechanism failed.")

    print("\n═══════════════════════════════════════════════")

if __name__ == "__main__":
    asyncio.run(run_demo())
