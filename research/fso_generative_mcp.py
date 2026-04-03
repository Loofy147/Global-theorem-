import asyncio
import hashlib
import json
import os
import sys
from typing import Dict, Any, Tuple, Optional, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We use the already populated transformers logic
import transformers

class GenerativeGate:
    """
    Acts as the 'Neural Logic' at specific coordinates.
    Synthesizes Hamiltonian sub-routines (scripts) using real LLMs from the Transformers library.
    """
    def __init__(self, model_id="gpt2"):
        print(f"[*] Initializing Generative Gate with model: {model_id}")
        # Use a small model that runs on CPU for the demo
        self.pipeline = transformers.pipeline("text-generation", model=model_id, device="cpu")

    async def synthesize_logic(self, prompt: str) -> str:
        """Calls the Transformers pipeline to produce a runnable Python function."""
        print(f"[*] Synthesizing logic for intent: '{prompt}'")

        full_prompt = f"# Python function for: {prompt}\ndef "
        output = self.pipeline(full_prompt, max_new_tokens=100, num_return_sequences=1, do_sample=True, temperature=0.7)
        generated_text = output[0]['generated_text']

        lines = generated_text.split('\n')
        code_lines = []
        in_func = False
        for line in lines:
            if line.startswith('def '): in_func = True
            if in_func:
                code_lines.append(line)
                if len(code_lines) > 1 and line.strip() and not line.startswith('    ') and not line.startswith('\t'):
                    break

        final_code = "\n".join(code_lines)
        if "return" not in final_code:
            final_code += "\n    return 'Executed generated logic'"

        return final_code

# --- THE MCP NODE (GENERATIVE VERSION) ---
class MCP_GenNode:
    def __init__(self, coords: Tuple[int, int, int], m: int, gate: Optional[GenerativeGate] = None):
        self.coords = coords
        self.m = m
        self.fiber = sum(coords) % m
        self.local_script_cache: Dict[str, Any] = {}
        self.gen_gate = gate if gate else GenerativeGate()
        self.local_storage: Dict[str, Any] = {}

    async def handle_wave(self, color: int, packet: Dict[str, Any]):
        if color == 1:
            task_id = packet.get("task_id")
            instruction = packet.get("instruction")
            data = packet.get("data")
            if task_id not in self.local_script_cache:
                raw_code = await self.gen_gate.synthesize_logic(instruction)
                try:
                    namespace = {}
                    exec(raw_code, namespace)
                    func_name = [k for k in namespace.keys() if not k.startswith('__')][0]
                    self.local_script_cache[task_id] = {"func": namespace[func_name], "code": raw_code, "id": task_id}
                except Exception as e:
                    fallback_code = f"def {task_id}_fallback(data):\n    return f'Fallback for {task_id}'"
                    namespace = {}
                    exec(fallback_code, namespace)
                    self.local_script_cache[task_id] = {"func": namespace[f"{task_id}_fallback"], "code": fallback_code, "id": task_id}
            logic_entry = self.local_script_cache[task_id]
            try:
                result = logic_entry["func"](data)
                return {"status": "SUCCESS", "node": self.coords, "task": task_id, "result": result, "type": "AUTOPOIETIC_EXECUTION", "code": logic_entry["code"]}
            except Exception as e:
                return {"status": "EXEC_ERROR", "reason": str(e)}
        return None

class FSOAutopoieticEngine:
    def __init__(self, m: int = 5, model_id: str = "gpt2"):
        self.m = m
        self.gate = GenerativeGate(model_id=model_id)
        self.nodes = { (x,y,z): MCP_GenNode((x,y,z), m, self.gate) for x in range(m) for y in range(m) for z in range(m) }

    async def execute_or_generate(self, task_id: str, instruction: str, data: Any, target_coords: Tuple[int, int, int]):
        packet = { "task_id": task_id, "instruction": instruction, "data": data }
        node = self.nodes[target_coords]
        return await node.handle_wave(color=1, packet=packet)
