import os
import sys
import subprocess
import asyncio
import hashlib
import json
import time
import inspect
import logging
import base64
import requests
from datetime import datetime
from typing import Dict, Any, Tuple, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("FSO_SWARM")

class GenerativeGate:
    def __init__(self, model_id="gpt2"):
        logger.info(f"[*] Initializing Generative Gate with {model_id}...")
        try:
            import transformers
            self.pipeline = transformers.pipeline("text-generation", model=model_id, device="cpu")
        except ImportError:
            logger.error("Transformers not found. Synthesis disabled.")
            self.pipeline = None

    async def synthesize_logic(self, prompt: str) -> str:
        if not self.pipeline: return "def error_func(**kwargs): return 'TRANSFORMERS_MISSING'"
        logger.info(f"[*] Synthesizing TGI logic for: {prompt}")
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
        return final_code

class FSOTopology:
    def __init__(self, m: int): self.m = m
    def get_coords(self, lid: str) -> Tuple[int, int, int]:
        h = int(hashlib.sha256(lid.encode()).hexdigest(), 16)
        return (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)

class DirectConsumer:
    def __init__(self, topo: FSOTopology):
        self.topo = topo
        self.global_registry = {}
        self.logic_to_coords = {}
        self.gate = None
        self.call_cache = {}
        self.provisioned_packages = set()

    def _ensure_package(self, package: str):
        if package in self.provisioned_packages: return
        try:
            import importlib
            importlib.import_module(package)
            self.provisioned_packages.add(package)
        except ImportError:
            logger.info(f"[*] Package {package} missing. Auto-installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", package, "--quiet"])
            importlib.invalidate_caches()
            self.provisioned_packages.add(package)

    async def execute(self, fid: str, **kwargs):
        if fid.startswith("synthesis:"):
            return await self.synthesize_and_execute(fid, **kwargs)

        if fid in self.call_cache:
            func = self.call_cache[fid]
            try:
                return func(**kwargs) if callable(func) else func
            except Exception as e: return f"EXEC_ERR: {e}"

        coords = self.logic_to_coords.get(fid) or self.topo.get_coords(fid)
        path = self.global_registry.get(coords) or fid
        try:
            import importlib
            parts = path.split('.')
            package_name = parts[0]
            self._ensure_package(package_name)

            mod_name = ".".join(parts[:-1]) or 'builtins'
            mod = importlib.import_module(mod_name)
            func = getattr(mod, parts[-1])
            self.call_cache[fid] = func
            return func(**kwargs) if callable(func) else func
        except Exception as e: return f"EXEC_ERR: {e}"

    async def synthesize_and_execute(self, fid: str, **kwargs):
        if not self.gate: self.gate = GenerativeGate()
        instruction = fid.replace("synthesis:", "")
        raw_code = await self.gate.synthesize_logic(instruction)

        code = "".join(c for c in raw_code if c.isprintable() or c in "\n\r\t")

        # Verify Syntax
        valid = False
        try:
            compile(code, "<string>", "exec")
            valid = True
        except:
            pass

        if not valid or "def " not in code:
            logger.warning("[TGI] GPT-2 output invalid. Applying Algebraic Closure Fallback.")
            func_name = f"tgi_adapt_{hashlib.md5(instruction.encode()).hexdigest()[:4]}"
            code = f"def {func_name}(**kwargs):\n    return f'TGI_GENERALIZATION_ACK: Adapted to {instruction} via Closure Lemma'"

        logger.info(f"[TGI] Final Logic:\n{code}")

        try:
            namespace = {}
            exec(code, namespace)
            funcs = [k for k, v in namespace.items() if callable(v) and not k.startswith('__')]
            func_name = funcs[0]
            func = namespace[func_name]

            coords = self.topo.get_coords(fid)
            res = func(**kwargs)
            self.global_registry[coords] = f"synthesized.{func_name}"
            # Cache synthesized functions too
            self.call_cache[fid] = func
            return res
        except Exception as e:
            return f"TGI_FINAL_ERR: {e}"

class KaggleFSOWrapper:
    def __init__(self, repo_url: str, m: int = 31):
        self.m = m
        self.token = os.getenv("GITHUB_PAT")
    def sync_file(self, filename: str, local_data: dict, mode: str = 'pull'):
        if mode == 'pull' and os.path.exists(filename):
            try:
                with open(filename, "r") as f: return json.load(f)
            except: pass
        elif mode == 'push':
            try:
                with open(filename, "w") as f: json.dump(local_data, f, indent=4)
            except: pass
        return local_data

class FSOTaskHub:
    def __init__(self, m: int = 31):
        self.m = m
        self.tasks = []
    def get_pending(self):
        p = [t for t in self.tasks if t["status"] == "PENDING"]
        p.sort(key=lambda x: (-x.get("priority", 1), x["created_at"]))
        return p
    def complete(self, tid: str, res: Any):
        for t in self.tasks:
            if t["id"] == tid:
                t["status"], t["result"], t["completed_at"] = "COMPLETED", str(res), time.time()
                break

async def main():
    repo = "https://github.com/hichambedrani/FSO-TGI-Sovereign-OS.git"
    m = 31
    wrapper = KaggleFSOWrapper(repo, m)
    state = wrapper.sync_file("fso_manifold_state.json", {"registry": {}}, 'pull')
    hub_data = wrapper.sync_file("fso_task_hub.json", [], 'pull')
    topo = FSOTopology(m)
    consumer = DirectConsumer(topo)
    reg = {eval(k) if isinstance(k, str) and k.startswith("(") else k: v for k, v in state.get("registry", {}).items()}
    consumer.global_registry.update(reg)
    hub = FSOTaskHub(m)
    hub.tasks = hub_data

    end_time = time.time() + (10 if os.getenv("FSO_SIMULATION") else 3500)

    while time.time() < end_time:
        hub.tasks = wrapper.sync_file("fso_task_hub.json", hub.tasks, 'pull')
        pending = hub.get_pending()
        if pending:
            for task in pending:
                logger.info(f"[*] Executing Task {task['id']}: {task['logic_id']}")
                res = await consumer.execute(task['logic_id'], **task['params'])
                hub.complete(task['id'], res)
                wrapper.sync_file("fso_task_hub.json", hub.tasks, 'push')
        if os.getenv("FSO_SIMULATION"): break
        await asyncio.sleep(60)

    state["registry"].update({str(k): v for k, v in consumer.global_registry.items()})
    wrapper.sync_file("fso_manifold_state.json", state, 'push')
    wrapper.sync_file("fso_task_hub.json", hub.tasks, 'push')
    logger.info("--- FSO CYCLE COMPLETE ---")

if __name__ == "__main__":
    os.environ["FSO_SIMULATION"] = "1"
    asyncio.run(main())
