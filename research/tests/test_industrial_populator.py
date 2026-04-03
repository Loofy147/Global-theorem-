import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_mesh_daemon import FSOMeshDaemon
from research.fso_industrial_populator import FSOIndustrialPopulator
from research.fso_fabric import COLOR_LOGIC

async def test_industrial_ingestion():
    print("Testing industrial ingestion...")
    daemon = FSOMeshDaemon(m=5)
    daemon.is_running = True
    populator = FSOIndustrialPopulator(daemon)

    await populator.ingest_repository("test_repo", "pixels")

    # Verify that logic is in the registry
    assert len(populator.logic_registry) > 0

    # Find a specific logic
    logic_id = "fft_convolution"
    coords = populator._get_fso_coords(logic_id)
    assert coords in populator.logic_registry

    # Verify it was injected into the node
    node = daemon.nodes[coords]
    assert logic_id in node.logic_registry
    print("Ingestion test passed!")

async def test_industrial_execution():
    print("Testing industrial execution...")
    daemon = FSOMeshDaemon(m=5)
    daemon.is_running = True
    populator = FSOIndustrialPopulator(daemon)

    await populator.ingest_repository("test_repo", "dist")

    logic_id = "load_balance_spike"
    target_coords = populator._get_fso_coords(logic_id)

    # Storage
    await daemon.inject_storage("key1", "data_state_x", target_coords)

    # Execution
    res = await daemon.execute_logic(logic_id, "key1", target_coords)
    assert res['status'] == "SUCCESS"
    assert "SPIKE_ROUTED" in res['result']['result']
    print("Execution test passed!")

async def run_all():
    try:
        await test_industrial_ingestion()
        await test_industrial_execution()
    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_all())
