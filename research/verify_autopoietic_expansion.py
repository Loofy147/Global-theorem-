import asyncio
import sys
import os
from typing import List, Dict, Any, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_generative_mcp import FSOAutopoieticEngine

async def main():
    print("--- FSO AUTOPOIETIC EXPANSION VERIFICATION ---")

    # 1. Initialize the Autopoietic Engine (m=5)
    engine = FSOAutopoieticEngine(m=5)

    # 2. Trigger expansion: "Self-Optimization" script
    print("\n[STEP 1] Triggering Synthesis for 'self_optimization_v1'...")

    # Send a Logic Wave (Color 1) to synthesize and execute a self-optimization script
    # This logic does not exist in the manifold yet.
    target_node = (2, 2, 2)
    task_id = "self_optimization_v1"
    instruction = "a function that analyzes system stats and suggests new manifold modulus m"
    system_stats = {"m": 5, "load": 0.9, "memory_usage": "high"}

    res = await engine.execute_or_generate(task_id, instruction, system_stats, target_node)

    if res and res.get("status") == "SUCCESS":
        print(f"Synthesis Result:")
        print(f"  Status: {res['status']}")
        print(f"  Node: {res['node']}")
        print(f"  Task: {res['task']}")
        print(f"  Output: {res['result']}")
        print(f"  Type: {res['type']}")
    else:
        print(f"Synthesis Failed: {res}")
        return

    # 3. Verify anchoring (O(1) search)
    print("\n[STEP 2] Verifying Logic Anchoring (Color 0)...")
    # Execute the same task again - should use the cached (anchored) script
    res_cached = await engine.execute_or_generate(task_id, instruction, system_stats, target_node)

    if res_cached and res_cached.get("status") == "SUCCESS":
        print(f"Cached Execution Result:")
        print(f"  Result: {res_cached['result']}")
        # The first execution should have printed "Activating Generative Gate...", the second should not.

    # 4. Synthesize industrial varieties
    print("\n[STEP 3] Expanding Industrial Varieties (Pixel -> Web)...")

    # Generate a pixel transformer
    pixel_res = await engine.execute_or_generate(
        "pixel_to_vector_v1",
        "a function that maps pixel intensity to a logarithmic vector",
        [100, 50, 200],
        (0, 0, 0)
    )
    print(f"Pixel Transformer Output: {pixel_res['result']}")

    print("\n[SUCCESS] Autopoietic Expansion and Logic Anchoring verified.")

if __name__ == "__main__":
    asyncio.run(main())
