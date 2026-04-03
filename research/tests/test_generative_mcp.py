import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_generative_mcp import FSOAutopoieticEngine, GenerativeGate

async def test_synthesis_anchoring():
    print("Testing Autopoietic Synthesis and Anchoring...")
    engine = FSOAutopoieticEngine(m=3)

    task_id = "test_task_1"
    instruction = "a function that adds 1 to data"
    target = (1, 1, 1)

    # 1. Synthesis and Execution
    res = await engine.execute_or_generate(task_id, instruction, 10, target)
    assert res['status'] == "SUCCESS"
    assert "Processed" in res['result']

    # 2. Anchoring check: logic_cache should have the task
    node = engine.nodes[target]
    assert task_id in node.local_script_cache

    # 3. Execution without re-synthesis
    # (Checking the output is sufficient, logic was already anchored)
    res2 = await engine.execute_or_generate(task_id, instruction, 20, target)
    assert res2['status'] == "SUCCESS"
    print("Synthesis/Anchoring test passed!")

async def test_generative_gate():
    print("Testing Generative Gate Mock logic...")
    gate = GenerativeGate()

    # Test specific mock patterns
    code_denoise = await gate.synthesize_logic("denoise pixels")
    assert "generated_denoiser" in code_denoise

    code_optimize = await gate.synthesize_logic("self_optimize system")
    assert "self_optimizer" in code_optimize
    print("Generative Gate test passed!")

async def run_all():
    try:
        await test_synthesis_anchoring()
        await test_generative_gate()
        print("All Generative MCP tests passed!")
    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_all())
