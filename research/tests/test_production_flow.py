import pytest
import asyncio
import os
import sys
import hashlib

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fso_executor import DirectConsumer, FSOTopology, FSOTaskHub
from research.fso_apex_hypervisor import FSO_Apex_Hypervisor

@pytest.mark.asyncio
async def test_end_to_end_production_logic():
    """
    Verifies that logic can be executed through the DirectConsumer
    without any simulation flags.
    """
    m = 31
    topo = FSOTopology(m)
    consumer = DirectConsumer(topo)

    # We'll use a synthesized function to test the full flow
    fid = "synthesis:test_add"

    # Mocking the gate to avoid downloading models
    class MockGate:
        async def synthesize_logic(self, prompt):
            return "def test_add(x, y):\n    return x + y"

    consumer.gate = MockGate()

    # Execute
    result = await consumer.execute(fid, x=10, y=5)
    assert result == 15

    # Test Task Hub Integration
    hub = FSOTaskHub(m)
    task_id = "test_task_001"
    hub.tasks.append({
        "id": task_id,
        "logic_id": fid,
        "params": {"x": 20, "y": 30},
        "status": "PENDING",
        "priority": 1,
        "created_at": 0
    })

    pending = hub.get_pending()
    assert len(pending) == 1

    task = pending[0]
    res = await consumer.execute(task['logic_id'], **task['params'])
    hub.complete(task['id'], res)

    assert hub.tasks[0]["status"] == "COMPLETED"
    assert hub.tasks[0]["result"] == "50"

@pytest.mark.asyncio
async def test_apex_stabilization_loop():
    """Verifies that the Hypervisor stabilization loop initializes correctly."""
    m = 11
    apex = FSO_Apex_Hypervisor(m=m)

    # Start loop in background
    task = asyncio.create_task(apex.run_stabilization_loop())
    await asyncio.sleep(0.5)

    # Check if loop is running (not cancelled)
    assert not task.done()

    # Cleanup
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
