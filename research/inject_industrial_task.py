import json
import time
import os
import hashlib

def inject_tasks():
    hub_path = "fso_task_hub.json"
    if os.path.exists(hub_path):
        with open(hub_path, "r") as f:
            tasks = json.load(f)
    else:
        tasks = []

    # Filter out completed tasks if needed
    tasks = [t for t in tasks if t.get("status") == "PENDING"]

    industrial_tasks = [
        {
            "id": hashlib.md5(f"vllm_ingest_{time.time()}".encode()).hexdigest()[:8],
            "logic_id": "transformers.pipeline",
            "params": {
                "task": "text-generation",
                "model": "gpt2"
            },
            "target": [0, 25, 4], # Example coord for logic synthesis
            "status": "PENDING",
            "priority": 20,
            "retry_count": 0,
            "created_at": time.time(),
            "updated_at": time.time()
        },
        {
            "id": hashlib.md5(f"ray_ingest_{time.time()}".encode()).hexdigest()[:8],
            "logic_id": "numpy.mean",
            "params": {
                "a": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
            },
            "target": [30, 25, 10],
            "status": "PENDING",
            "priority": 15,
            "retry_count": 0,
            "created_at": time.time(),
            "updated_at": time.time()
        }
    ]

    tasks.extend(industrial_tasks)

    with open(hub_path, "w") as f:
        json.dump(tasks, f, indent=4)

    print(f"[+] Injected {len(industrial_tasks)} industrial ingestion tasks into {hub_path}.")

if __name__ == "__main__":
    inject_tasks()
