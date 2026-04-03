import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_mesh_daemon import FSOMeshDaemon
from research.fso_industrial_populator import FSOIndustrialPopulator
from research.fso_fabric import COLOR_LOGIC

async def test_full_pipeline():
    print("Testing Full Production Pipeline (m=5)...")
    daemon = FSOMeshDaemon(m=5)

    # 1. Bootstrap
    await daemon.bootstrap(["./research/fso_fabric.py"])
    assert len(daemon.populator.logic_inventory) > 0

    # 2. Industrial Variety
    populator = FSOIndustrialPopulator(daemon)
    await populator.ingest_repository("test", "pixels")
    assert "fft_convolution" in [m['id'] for m in populator.logic_registry.values()]

    # 3. Autopoietic Synthesis
    target = (1, 1, 1)
    task_id = "test_gen_task"
    instruction = "a function that returns data * 2"

    packet = {
        "color": COLOR_LOGIC,
        "target": target,
        "payload": {
            "id": task_id,
            "instruction": instruction,
            "data": 42
        }
    }

    res = await daemon.handle_request(packet)
    assert res['status'] == "SUCCESS"
    assert "Synthesized Logic Result" in res['result']['result']

    print("Full Pipeline Test Passed!")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
