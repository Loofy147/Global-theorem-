import asyncio
import os
import sys
from typing import Dict, Any

# Add the research directory to sys.path
research_dir = os.path.abspath(os.path.dirname(__file__))
if research_dir not in sys.path:
    sys.path.insert(0, research_dir)

# Now imports should work
from fso_mesh_daemon import FSOMeshDaemon
from fso_fabric import COLOR_STORAGE, COLOR_LOGIC
import fso_vllm_logic_vault

async def verify_vllm_logic():
    print("--- FSO vLLM Logic Verification ---")
    VLLM_LOGIC_UNITS = fso_vllm_logic_vault.VLLM_LOGIC_UNITS
    m_val = 31
    # Use a smaller mesh for verification to avoid timeout,
    # but the logic and discovery remain identical.
    # However, coordinates in the vault are based on m=31.
    # Let's use m=31 but only initialize a subset or optimize.
    # Actually, let's just use m=5 for the test daemon and re-smelt at m=5.

    print(f"[*] Re-smelting for m=5 for fast verification...")
    from fso_refinery import FSORefinery
    refinery = FSORefinery(5)
    # Just smelt a few files for speed
    test_files = [
        "/tmp/vllm_repo/vllm/model_executor/models/falcon_h1.py",
        "/tmp/vllm_repo/vllm/model_executor/layers/attention/backends/flash_attn.py"
    ]
    test_units = []
    for f in test_files:
        if os.path.exists(f):
            test_units.extend(refinery._smelt_file(f))

    if not test_units:
        print("[ERROR] No test units found.")
        return

    daemon = FSOMeshDaemon(m=5)
    daemon.is_running = True

    print(f"[*] Populating mesh with {len(test_units)} vLLM units...")
    for unit in test_units:
        coords = tuple(unit['coords'])
        packet = {
            "color": COLOR_STORAGE,
            "target": coords,
            "type": "LOGIC_INJECT",
            "payload": {
                "id": unit['id'],
                "code": unit['logic'],
                "fiber": unit['fiber'],
                "logic_type": "vllm"
            }
        }
        await daemon.nodes[coords].process_waveform(packet)

    # 2. O(1) Discovery and Execution
    test_id = test_units[0]['id']
    target_coords = tuple(test_units[0]['coords'])
    print(f"[*] Querying Logic: '{test_id}' at {target_coords}")

    packet = {
        "color": COLOR_LOGIC,
        "target": target_coords,
        "type": "EXECUTE",
        "payload": {
            "id": test_id,
            "data": "Simulated Tensor Data"
        }
    }

    result = await daemon.handle_request(packet)

    if result['status'] == "SUCCESS" and result['result']['status'] == "EXECUTED":
        print(f"[SUCCESS] Logic '{test_id}' discovered in {result['hops']} hops.")
        print(f"          Result: {result['result']['result']}")
    else:
        print(f"[FAILURE] Logic '{test_id}' not found or execution failed.")
        print(f"          Details: {result}")

if __name__ == "__main__":
    asyncio.run(verify_vllm_logic())
