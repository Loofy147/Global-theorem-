import json
import os
import hashlib
import time
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger("TASK_HUB")

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
        try:
            with open(self.hub_file, "w") as f:
                json.dump(self.tasks, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save task hub: {e}")

    def add_task(self, logic_id: str, params: Dict[str, Any], priority: int = 1):
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
            "priority": priority,
            "retry_count": 0,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        self.tasks.append(task)
        self.save_hub()
        return task_id

    def get_pending_tasks(self, role: str) -> List[Dict[str, Any]]:
        # Sort by priority (higher value first) and creation time
        pending = [t for t in self.tasks if t["status"] == "PENDING"]
        pending.sort(key=lambda x: (-x.get("priority", 1), x["created_at"]))
        return pending

    def complete_task(self, task_id: str, result: Any):
        for t in self.tasks:
            if t["id"] == task_id:
                t["status"] = "COMPLETED"
                t["result"] = result
                t["completed_at"] = time.time()
                t["updated_at"] = time.time()
                break
        self.save_hub()

    def cleanup_stale_tasks(self, timeout_seconds: int = 3600):
        """Resets tasks that have been 'PENDING' for too long or handles retries."""
        now = time.time()
        changed = False
        for t in self.tasks:
            if t["status"] == "PENDING" and (now - t["created_at"]) > timeout_seconds:
                if t.get("retry_count", 0) < 3:
                    t["retry_count"] += 1
                    t["created_at"] = now # Reset timer for retry
                    t["updated_at"] = now
                    logger.info(f"Retrying stale task {t['id']}")
                    changed = True
                else:
                    t["status"] = "FAILED"
                    t["reason"] = "STALE_TIMEOUT"
                    t["updated_at"] = now
                    logger.warning(f"Task {t['id']} marked as FAILED due to timeout.")
                    changed = True

        if changed:
            self.save_hub()

if __name__ == "__main__":
    hub = FSOTaskHub()
    tid = hub.add_task("math.sqrt", {"x": 144}, priority=10)
    print(f"Added task {tid}")
    print(f"Pending: {hub.get_pending_tasks('EXECUTOR')}")
