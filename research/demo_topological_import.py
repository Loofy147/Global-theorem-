import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_fabric import FSOFabricNode, COLOR_LOGIC, FSODataStream, FSODirectConsumer

async def run_demo():
    print("═══════════════════════════════════════════════")
    print("  FSO TOPOLOGICAL SELF-IMPORT DEMONSTRATION  ")
    print("═══════════════════════════════════════════════")

    m_val = 31
    dc = FSODirectConsumer(m_val)

    # 1. Load the Manifest
    manifest_path = "research/fso_production_manifest.json"
    if not os.path.exists(manifest_path):
        print("[!] Manifest missing. Running self-populator...")
        os.system("python3 research/fso_self_populate.py")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # 2. Setup a virtual mesh for the demo
    mesh = {}

    # Anchor the actual project.core.verify_sigma logic
    logic_id = "project.core.verify_sigma"
    # DYNAMICALLY RESOLVE COORDS from DirectConsumer
    coords = dc.get_coords(logic_id)
    print(f"[*] Resolving '{logic_id}' to manifold coord: {coords}")

    core_node = FSOFabricNode(coords, m_val)
    core_node.mesh_nodes = mesh
    core_node.logic_registry[logic_id] = {
        "id": logic_id,
        "code": manifest[logic_id]["code"],
        "type": "project_logic"
    }
    mesh[coords] = core_node

    # Setup the Self-Importer logic
    importer_id = "project.demo.self_importer"
    importer_coords = (1, 2, 3)
    importer_node = FSOFabricNode(importer_coords, m_val)
    importer_node.mesh_nodes = mesh

    self_import_logic = """
async def self_importer(data):
    print(f"  [SelfImporter] Received data: {data}")
    # FUNCTIONAL TOPOLOGICAL CALL: Resolves and executes logic from another coordinate
    result = await topological_call("project.core.verify_sigma", {"sigma": {}})
    return f"COMPLEX_PROCESS_COMPLETE: {result}"
"""
    importer_node.logic_registry[importer_id] = {
        "id": importer_id,
        "code": self_import_logic,
        "type": "project_logic"
    }
    mesh[importer_coords] = importer_node

    # 3. Trigger the Logic Wave
    print(f"\n[*] Triggering Logic Wave for '{importer_id}' at {importer_coords}...")

    packet = FSODataStream.create_packet(
        {"id": importer_id, "data": "Test_Data_123"},
        importer_coords,
        color=COLOR_LOGIC
    )

    res = await importer_node.route_packet(packet)

    print("\n[RESULT]:")
    print(json.dumps(res, indent=4))

    # Verify that the result is functional, not a mock
    if res.get("status") == "EXECUTED" and "EXECUTED_GENERIC_SPEC" in res.get("result", ""):
        print("\n[SUCCESS] Functional Topological Self-Import Verified!")
        print("The FSO node successfully resolved and executed logic from another manifold node.")
    else:
        print("\n[FAILURE] Self-import mechanism failed or returned a mock string.")

    print("\n═══════════════════════════════════════════════")

if __name__ == "__main__":
    asyncio.run(run_demo())
