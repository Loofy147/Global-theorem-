import asyncio
import hashlib
import json
import os
import sys
from typing import Dict, Any, Tuple, Optional, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- FSO GENERATIVE KERNEL ---
class GenerativeGate:
    """
    Acts as the 'Neural Logic' at specific coordinates.
    Synthesizes Hamiltonian sub-routines (scripts) on the fly.
    """
    def __init__(self):
        # In a real production environment, this would be a secure API key
        self.api_key = os.getenv("GEMINI_API_KEY", "DEMO_KEY")

    async def synthesize_logic(self, prompt: str) -> str:
        """Calls the generative model to produce a runnable Python function."""
        # print(f"[*] Synthesizing logic for: '{prompt}'...")

        # Simulate the generative process with a high-fidelity mock
        # In production: fetch("https://generativelanguage.googleapis.com/v1beta/models/...")
        await asyncio.sleep(0.5) # Simulate network latency

        # Mock logic based on common industrial prompts
        if "denoise" in prompt.lower():
            return "def generated_denoiser(pixels):\n    return [p if p > 10 and p < 245 else 128 for p in pixels]"
        elif "self_optimize" in prompt.lower():
            return "def self_optimizer(stats):\n    return {'new_m': stats.get('m', 11) + 2, 'status': 'Optimized'}"
        elif "pixel_to_vector" in prompt.lower():
            return "def pixel_to_vector(p):\n    import math\n    return [math.sqrt(x) for x in p]"

        return "def generic_logic(data):\n    return f'Processed via FSO Generative Gate: {data}'"

# --- THE MCP NODE (GENERATIVE VERSION) ---
class MCP_GenNode:
    """
    A 'Generative Node' in the FSO Autopoietic Engine.
    Can author its own connectivity by synthesizing missing logic.
    """
    def __init__(self, coords: Tuple[int, int, int], m: int):
        self.coords = coords
        self.m = m
        self.fiber = sum(coords) % m

        # Local Logic Inventory (Holographic Layer)
        self.local_script_cache: Dict[str, Any] = {}
        self.gen_gate = GenerativeGate()
        self.local_storage: Dict[str, Any] = {}

    async def handle_wave(self, color: int, packet: Dict[str, Any]):
        """
        Color 1 (Logic Wave) now triggers 'Autopoietic Expansion' if logic is missing.
        """
        if color == 1: # LOGIC / INSTRUCTION WAVE
            task_id = packet.get("task_id")
            instruction = packet.get("instruction")
            data = packet.get("data")

            if task_id not in self.local_script_cache:
                print(f"[Node {self.coords}] Logic '{task_id}' missing in manifold. Activating Generative Gate...")
                raw_code = await self.gen_gate.synthesize_logic(instruction)

                # 1. GENERATE: Compile the logic into a live object
                try:
                    namespace = {}
                    exec(raw_code, namespace)
                    # Extract the first function defined in the namespace
                    func_name = [k for k in namespace.keys() if not k.startswith('__')][0]
                    self.local_script_cache[task_id] = {
                        "func": namespace[func_name],
                        "code": raw_code,
                        "id": task_id
                    }
                    print(f"[Node {self.coords}] Logic '{task_id}' synthesized and anchored into RAM.")
                except Exception as e:
                    print(f"[Node {self.coords}] Synthesis Failure: {e}")
                    return {"status": "ERROR", "reason": str(e)}

            # 2. EXECUTE: Run the newly created (or cached) logic
            logic_entry = self.local_script_cache[task_id]
            try:
                result = logic_entry["func"](data)
                return {
                    "status": "SUCCESS",
                    "node": self.coords,
                    "task": task_id,
                    "result": result,
                    "type": "AUTOPOIETIC_EXECUTION"
                }
            except Exception as e:
                return {"status": "EXEC_ERROR", "reason": str(e)}

        elif color == 0: # STORAGE WAVE
            key = packet.get("key")
            val = packet.get("val")
            self.local_storage[key] = val
            return {"status": "STORED"}

        return None

# --- AUTOPOIETIC ENGINE ---
class FSOAutopoieticEngine:
    def __init__(self, m: int = 5):
        self.m = m
        self.nodes = { (x,y,z): MCP_GenNode((x,y,z), m) for x in range(m) for y in range(m) for z in range(m) }

    async def execute_or_generate(self, task_id: str, instruction: str, data: Any, target_coords: Tuple[int, int, int]):
        """Injects a Logic Wave into the manifold."""
        packet = {
            "task_id": task_id,
            "instruction": instruction,
            "data": data
        }

        # In a real manifold, this would be a Hamiltonian route.
        # Here we directly target the node to demonstrate the generative logic.
        node = self.nodes[target_coords]
        return await node.handle_wave(color=1, packet=packet)

async def demo():
    engine = FSOAutopoieticEngine(m=5)

    print("--- FSO AUTOPOIETIC ENGINE INITIATING ---")

    # Task 1: Generate a denoiser
    res1 = await engine.execute_or_generate(
        "denoise_v1",
        "a function that removes outliers from pixel values",
        [255, 0, 10, 200, 248, 5],
        (1, 1, 1)
    )
    print(f"Result 1: {res1}")

    # Task 2: Generate a self-optimizer
    res2 = await engine.execute_or_generate(
        "self_optimize_v1",
        "a function that analyzes system stats and suggests new manifold modulus m",
        {"m": 5, "load": 0.9},
        (2, 2, 2)
    )
    print(f"Result 2: {res2}")

if __name__ == "__main__":
    asyncio.run(demo())
