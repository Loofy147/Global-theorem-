import asyncio
import os
import sys
import time
import logging
from typing import Tuple

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research.fso_apex_hypervisor import FSO_Apex_Hypervisor
from research.fso_evolution_engine import FSO_Evolution_Engine, TopologicalGravity

async def test_end_to_end():
    print("\n--- FSO APEX & EVOLUTION END-TO-END TEST ---")
    m = 5
    apex = FSO_Apex_Hypervisor(m=m)
    engine = FSO_Evolution_Engine(apex)

    # 1. Test Library Ingestion
    print("\n[Step 1] Testing Library Ingestion...")
    # Use 'math' instead of 'numpy' as it's guaranteed to be available and faster to inspect
    apex.consumer.auto_provision("math")

    # Verify mapping
    logic_id = "math.sqrt"
    coords = apex.topo.get_coords(logic_id)
    print(f"Logic '{logic_id}' mapped to {coords}")
    assert coords in apex.consumer.global_registry

    # 2. Test Execution via Hypervisor
    print("\n[Step 2] Testing Execution via Hypervisor...")
    result = await apex.command_execution(logic_id, 100)
    print(f"Result of math.sqrt(100): {result}")
    assert result == 10.0

    # 3. Test Topological Gravity calculations
    print("\n[Step 3] Testing Topological Gravity...")
    gravity = TopologicalGravity(m=m)
    p1 = (0, 0, 0)
    p2 = (2, 2, 2)
    dist = gravity.calculate_distance(p1, p2)
    print(f"Distance between {p1} and {p2} (m={m}): {dist}")
    assert dist == 6 # |2-0| + |2-0| + |2-0|

    # 4. Test Evolution Engine & Drift
    print("\n[Step 4] Testing Evolution Engine & Drift...")
    # Suppose a caller at (0,0,0) frequently calls logic at (2,2,2)
    test_logic_id = "math.sin"
    initial_coords = apex.topo.get_coords(test_logic_id)
    caller_coords = (0, 0, 0)

    print(f"Caller at {caller_coords}, Logic at {initial_coords}")

    # Execute and evolve
    await engine.evaluate_and_evolve(test_logic_id, caller_coords, 0)

    # Verify drift occurred if distance was > 1
    initial_dist = gravity.calculate_distance(initial_coords, caller_coords)

    evolved_coords = None
    for c, lid in apex.consumer.global_registry.items():
        if lid == test_logic_id:
            evolved_coords = c
            break

    print(f"Evolved coords for '{test_logic_id}': {evolved_coords}")
    if initial_dist > 1:
        assert evolved_coords != initial_coords
        assert gravity.calculate_distance(evolved_coords, caller_coords) < initial_dist

    # 5. Test Healing via Hypervisor
    print("\n[Step 5] Testing Hypervisor Healing...")
    apex.health_map[evolved_coords] = False
    print(f"Node {evolved_coords} marked as dead.")

    # Execution should trigger auto-heal
    await apex.command_execution(test_logic_id, 0)
    assert apex.health_map[evolved_coords] == True

    print("\n[SUCCESS] All end-to-end tests passed!")

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
