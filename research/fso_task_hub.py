import json
import os
import hashlib
import time
from typing import Dict, List, Any, Tuple

class FSOTaskHub:
    def __init__(self, hub_file: str = "fso_task_hub.json", m: int = 31):
        self.hub_file = hub_file
        self.m = m
        self.tasks = self._load_hub()

    def _load_hub(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.hub_file):
            try:
                with open(self.hub_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_hub(self):
        with open(self.hub_file, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def add_task(self, logic_id: str, params: Dict[str, Any]):
        task_id = hashlib.md5(f"{logic_id}{params}{time.time()}".encode()).hexdigest()[:8]
        # Spike Routing: Assign a target coordinate for the task
        h = int(hashlib.sha256(logic_id.encode()).hexdigest(), 16)
        target = (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)

        task = {
            "id": task_id,
            "logic_id": logic_id,
            "params": params,
            "target": target,
            "status": "PENDING",
            "created_at": time.time()
        }
        self.tasks.append(task)
        self.save_hub()
        return task_id

    def get_pending_tasks(self, role: str) -> List[Dict[str, Any]]:
        # For simplicity, in this distributed environment, we filter by status
        return [t for t in self.tasks if t["status"] == "PENDING"]

    def complete_task(self, task_id: str, result: Any):
        for t in self.tasks:
            if t["id"] == task_id:
                t["status"] = "COMPLETED"
                t["result"] = result
                t["completed_at"] = time.time()
                break
        self.save_hub()

if __name__ == "__main__":
    hub = FSOTaskHub()
    tid = hub.add_task("math.sqrt", {"x": 144})
    print(f"Added task {tid}")
    print(f"Pending: {hub.get_pending_tasks('EXECUTOR')}")
