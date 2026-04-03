import asyncio
import os
import sys
import json
import torch

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from fso_mesh_daemon import FSOMeshDaemon
from fso_fabric import COLOR_LOGIC, FSOFabricNode

async def test_production_manifest():
    print("--- FSO Production Manifest Test (PyTorch) ---")
    m_val = 31
    # We'll instantiate only the target node to avoid O(m^3) overhead in the demo
    target_coords = (1, 26, 23) # Manifest coordinate for torch.nn.ReLU
    node = FSOFabricNode(target_coords, m_val)

    # 1. Input Data
    mock_tensor = torch.randn(2, 2)
    print(f"[*] Input Tensor:\n{mock_tensor}")

    # 2. Logic Wave Payload
    call_spec = "torch.nn.ReLU"
    packet = {
        "color": COLOR_LOGIC,
        "target": target_coords,
        "type": "DIRECT_CALL",
        "payload": {
            "call_spec": call_spec,
            "data": {} # Just instantiate ReLU()
        }
    }

    print(f"[*] Processing Direct Industrial Logic wave at node {target_coords}...")
    result = await node.process_waveform(packet)

    if result['status'] == "EXECUTED":
        relu_instance = result['result']
        print(f"[SUCCESS] Class '{call_spec}' instantiated via FSO Node.")
        print(f"          Instance type: {type(relu_instance)}")

        # Now apply the instantiated logic
        if isinstance(relu_instance, torch.nn.ReLU):
            output = relu_instance(mock_tensor)
            print(f"          Output Tensor (ReLU applied):\n{output}")
    else:
        print(f"[FAILURE] Direct Logic execution failed.")
        print(f"          Details: {result}")

if __name__ == "__main__":
    asyncio.run(test_production_manifest())
