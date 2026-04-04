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
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("FSO_SWARM")

class FSOTopology:
    def __init__(self, m: int): self.m = m
    def get_coords(self, lid: str) -> Tuple[int, int, int]:
        h = int(hashlib.sha256(lid.encode()).hexdigest(), 16)
        return (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)

class StratifiedMemory:
    """FSO Stratified Memory for O(1) recall at sqrt(F) capacity."""
    def __init__(self, dim=1024, m_fibers=101):
        self.dim = dim
        self.m = m_fibers
        self.traces = {f: np.zeros(dim) for f in range(m_fibers)}

    def _get_fiber(self, key: str) -> int:
        h = hashlib.sha256(key.encode()).digest()
        return sum(h[:3]) % self.m

    def bind_store(self, key_vec: np.ndarray, val_vec: np.ndarray, key_str: str):
        fiber = self._get_fiber(key_str)
        # Circular convolution via FFT
        binding = np.fft.ifft(np.fft.fft(key_vec) * np.fft.fft(val_vec)).real
        self.traces[fiber] += binding

    def unbind_recall(self, key_vec: np.ndarray, key_str: str) -> np.ndarray:
        fiber = self._get_fiber(key_str)
        trace = self.traces[fiber]
        # Retrieval via FFT Complex Conjugate (Theorem 4.2)
        return np.fft.ifft(np.fft.fft(trace) * np.conj(np.fft.fft(key_vec))).real

class DirectConsumer:
    def __init__(self, topo: FSOTopology):
        self.topo = topo
        self.global_registry = {}
        self.logic_to_coords = {}
        self.memory = StratifiedMemory(m_fibers=topo.m)

    def auto_provision(self, package: str):
        logger.info(f"[*] Provisioning {package}...")
        try:
            import importlib
            module = importlib.import_module(package)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", package, "--quiet"])
            importlib.invalidate_caches()
            module = importlib.import_module(package)
        count = 0
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) or inspect.isbuiltin(obj):
                fid = f"{package}.{name}"
                coords = self.topo.get_coords(fid)
                self.global_registry[coords] = fid
                self.logic_to_coords[fid] = coords
                count += 1
        logger.info(f"[+] Anchored {count} units for {package}.")

    def execute(self, fid: str, **kwargs):
        coords = self.logic_to_coords.get(fid) or self.topo.get_coords(fid)
        path = self.global_registry.get(coords) or fid
        try:
            import importlib
            parts = path.split('.')
            mod_name = ".".join(parts[:-1]) or 'builtins'
            mod = importlib.import_module(mod_name)
            func = getattr(mod, parts[-1])
            return func(*kwargs.values()) if callable(func) else func
        except Exception as e: return f"EXEC_ERR: {e}"

class KaggleFSOWrapper:
    def __init__(self, repo_url: str, m: int = 101):
        parts = repo_url.replace(".git", "").split("/")
        self.owner, self.name = parts[-2], parts[-1]
        self.m = m
        self.token = os.getenv("GITHUB_PAT")
        self.api_base = f"https://api.github.com/repos/{self.owner}/{self.name}/contents"

    def sync_file(self, filename: str, local_data: dict, mode: str = 'pull'):
        if not self.token: return local_data
        headers = {"Authorization": f"token {self.token}", "Accept": "application/vnd.github.v3+json"}
        url = f"{self.api_base}/{filename}"

        if mode == 'pull':
            try:
                res = requests.get(url, headers=headers)
                if res.status_code == 200:
                    return json.loads(base64.b64decode(res.json()['content']).decode())
            except: pass
            return local_data
        else:
            try:
                sha = None
                curr = requests.get(url, headers=headers)
                if curr.status_code == 200: sha = curr.json().get('sha')
                data = {"message": f"FSO Sync {filename}: {datetime.now().isoformat()}", "content": base64.b64encode(json.dumps(local_data, indent=4).encode()).decode()}
                if sha: data["sha"] = sha
                requests.put(url, headers=headers, json=data)
            except: pass
            return local_data

class FSOTaskHub:
    def __init__(self, m: int = 101):
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
    role = os.getenv("FSO_ROLE", "INGESTOR")
    repo = "https://github.com/hichambedrani/Global-theorem-.git"
    m = 101

    wrapper = KaggleFSOWrapper(repo, m)
    state = wrapper.sync_file("fso_manifold_state.json", {"registry": {}}, 'pull')
    hub_data = wrapper.sync_file("fso_task_hub.json", [], 'pull')

    topo = FSOTopology(m)
    consumer = DirectConsumer(topo)
    # Convert string keys to tuples for internal registry
    registry = {}
    for k, v in state.get("registry", {}).items():
        try:
            if k.startswith("("):
                coords = tuple(map(int, k.strip("()").split(", ")))
                registry[coords] = v
            else: registry[k] = v
        except: registry[k] = v

    consumer.global_registry.update(registry)

    hub = FSOTaskHub(m)
    hub.tasks = hub_data

    end_time = time.time() + 3500

    if role == "INGESTOR":
        libs = ["transformers", "datasets", "torch", "numpy", "vllm", "ray"]
        for lib in libs:
            consumer.auto_provision(lib)
            await asyncio.sleep(1)

    elif role == "EXECUTOR":
        while time.time() < end_time:
            hub.tasks = wrapper.sync_file("fso_task_hub.json", hub.tasks, 'pull')
            pending = hub.get_pending()
            if pending:
                for task in pending:
                    logger.info(f"[*] Executing Task {task['id']}: {task['logic_id']}")
                    res = consumer.execute(task['logic_id'], **task['params'])
                    hub.complete(task['id'], res)
                    wrapper.sync_file("fso_task_hub.json", hub.tasks, 'push')
            await asyncio.sleep(60)

    elif role == "STABILIZER":
        while time.time() < end_time:
            state["registry"]["system.health"] = "OK"
            state["registry"]["system.last_check"] = datetime.now().isoformat()
            # Stringify keys for JSON compatibility
            state["registry"].update({str(k): v for k, v in consumer.global_registry.items()})
            wrapper.sync_file("fso_manifold_state.json", state, 'push')
            await asyncio.sleep(300)

    # Final Persist
    state["registry"].update({str(k): v for k, v in consumer.global_registry.items()})
    wrapper.sync_file("fso_manifold_state.json", state, 'push')
    wrapper.sync_file("fso_task_hub.json", hub.tasks, 'push')
    logger.info(f"--- FSO {role} CYCLE COMPLETE ---")

if __name__ == "__main__":
    # Ensure credentials are set
    if not os.getenv("GITHUB_PAT"):
        os.environ["GITHUB_PAT"] = "github_pat_11BKWH6MI0mIzqUWKHyxEX_KO92xoWx25JHq96tT4DK64FlhWr3gOO57S0XBmeg8bNS662LXRE85uyIE5"
    asyncio.run(main())
