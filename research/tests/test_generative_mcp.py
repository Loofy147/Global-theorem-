import asyncio
import os
import sys
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_generative_mcp import FSOAutopoieticEngine, GenerativeGate

async def test_synthesis_anchoring():
    print("Testing Autopoietic Synthesis and Anchoring...")

    # Mock the transformers pipeline to return predictable code
    mock_pipeline = MagicMock()
    mock_pipeline.return_value = [{'generated_text': "def process_data(data):\n    return f'Processed {data}'"}]

    with patch('transformers.pipeline', return_value=mock_pipeline):
        engine = FSOAutopoieticEngine(m=3)

        task_id = "test_task_1"
        instruction = "a function that adds 1 to data"
        target = (1, 1, 1)

        # 1. Synthesis and Execution
        res = await engine.execute_or_generate(task_id, instruction, 10, target)
        assert res['status'] == "SUCCESS"
        assert "Processed" in str(res['result'])

        # 2. Anchoring check: logic_cache should have the task
        node = engine.nodes[target]
        assert task_id in node.local_script_cache

        # 3. Execution without re-synthesis
        res2 = await engine.execute_or_generate(task_id, instruction, 20, target)
        assert res2['status'] == "SUCCESS"
        assert "Processed 20" in res2['result']
        print("Synthesis/Anchoring test passed!")

async def test_generative_gate():
    print("Testing Generative Gate Mock logic...")

    mock_pipeline = MagicMock()
    # Return different code for different prompts to satisfy the test assertions
    def side_effect(prompt, **kwargs):
        if "denoise" in prompt:
            return [{'generated_text': "def generated_denoiser(x):\n    return x"}]
        if "optimize" in prompt:
            return [{'generated_text': "def self_optimizer(x):\n    return x"}]
        return [{'generated_text': "def generic(x):\n    return x"}]

    mock_pipeline.side_effect = side_effect

    with patch('transformers.pipeline', return_value=mock_pipeline):
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_all())
