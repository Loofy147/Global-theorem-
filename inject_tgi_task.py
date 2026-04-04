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

    anomaly_data = {
        "topology": "CHATIC_GRID_v1",
        "path": "kaggle_data/novel_anomaly.json"
    }

    task_id = hashlib.md5(f"synthesis:adapt_to_anomaly{anomaly_data}{time.time()}".encode()).hexdigest()[:8]

    # Target coordinate for synthesis logic
    m = 31
    lid = "synthesis:adapt_to_anomaly"
    h = int(hashlib.sha256(lid.encode()).hexdigest(), 16)
    target = (h % m, (h // m) % m, (h // (m**2)) % m)

    new_task = {
        "id": task_id,
        "logic_id": lid,
        "params": {"data": anomaly_data},
        "target": target,
        "status": "PENDING",
        "priority": 20, # Ultra-high priority for TGI
        "retry_count": 0,
        "created_at": time.time(),
        "updated_at": time.time()
    }

    tasks.insert(0, new_task) # Prepend to ensure it's picked up first

    with open(hub_file, "w") as f:
        json.dump(tasks, f, indent=4)

    print(f"[*] Injected TGI Task {task_id} at {target}")

if __name__ == "__main__":
    inject()
