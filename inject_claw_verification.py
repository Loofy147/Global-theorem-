import json
import os
import hashlib
import time

def inject():
    hub_file = "fso_task_hub.json"
    if os.path.exists(hub_file):
        with open(hub_file, "r") as f:
            tasks = json.load(f)
    else:
        tasks = []

    lid = "claw.tools.render_tool_index"
    m = 31
    h = int(hashlib.sha256(lid.encode()).hexdigest(), 16)
    target = (h % m, (h // m) % m, (h // (m**2)) % m)

    task_id = hashlib.md5(f"{lid}{time.time()}".encode()).hexdigest()[:8]

    new_task = {
        "id": task_id,
        "logic_id": lid,
        "params": {"tools": []},
        "target": target,
        "status": "PENDING",
        "priority": 15,
        "retry_count": 0,
        "created_at": time.time(),
        "updated_at": time.time()
    }

    tasks.insert(0, new_task)

    with open(hub_file, "w") as f:
        json.dump(tasks, f, indent=4)

    print(f"[*] Injected Claw Verification Task {task_id} at {target}")

if __name__ == "__main__":
    inject()
