import asyncio
import os
import sys
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_mesh_daemon import FSOMeshDaemon
from research.fso_fabric import COLOR_LOGIC

async def test_skimage_direct():
    print("--- FSO Direct Consumption Test (scikit-image) ---")
    m_val = 5
    daemon = FSOMeshDaemon(m=m_val)
    daemon.is_running = True

    # 1. Define the 'Visual Industry' task
    # Note: Package is scikit-image, but module is skimage
    call_spec = "skimage.filters.sobel"

    # Map the logic to its coordinate
    from research.fso_direct_consumer import FSODirectConsumer
    dc = FSODirectConsumer(m_val)
    target_coords = dc.get_coords(call_spec)

    print(f"[*] Logic '{call_spec}' mapped to {target_coords}")

    # Create a mock 10x10 image (normalized)
    mock_image = np.random.rand(10, 10)

    # 2. Trigger the Logic Wave (Color 1)
    packet = {
        "color": COLOR_LOGIC,
        "target": target_coords,
        "type": "DIRECT_CALL",
        "payload": {
            "call_spec": call_spec,
            "data": {"image": mock_image}
        }
    }

    print(f"[*] Sending Logic Wave to {target_coords}...")
    result = await daemon.handle_request(packet)

    if result['status'] == "SUCCESS" and result['result']['status'] == "EXECUTED":
        res_data = result['result']['result']
        if isinstance(res_data, str) and "DIRECT_EXEC_ERROR" in res_data:
             print(f"[FAILURE] Direct Logic execution failed.")
             print(f"          Error: {res_data}")
        else:
            print(f"[SUCCESS] Direct Logic '{call_spec}' executed.")
            print(f"          Result type: {type(res_data)}")
            if isinstance(res_data, np.ndarray):
                print(f"          Result shape: {res_data.shape}")
            print(f"          Discovery hops: {result['hops']}")
    else:
        print(f"[FAILURE] Direct Logic execution failed.")
        print(f"          Details: {result}")

if __name__ == "__main__":
    asyncio.run(test_skimage_direct())
