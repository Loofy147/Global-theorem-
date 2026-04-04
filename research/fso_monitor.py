import os
import subprocess
import json
import time
from datetime import datetime

class FSOMonitor:
    def __init__(self, kernels: list):
        self.kernels = kernels
        self.state_file = "fso_manifold_state.json"
        self.hub_file = "fso_task_hub.json"

    def check_kaggle_status(self):
        print(f"\n--- KAGGLE KERNEL STATUS ({datetime.now().strftime('%H:%M:%S')}) ---")
        for k in self.kernels:
            try:
                res = subprocess.check_output(["kaggle", "kernels", "status", k]).decode().strip()
                print(f"  [{k}] {res}")
            except:
                print(f"  [{k}] Error checking status")

    def check_manifold_health(self):
        print("\n--- MANIFOLD HEALTH ---")
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
                last_check = state.get("registry", {}).get("system.last_check", "N/A")
                health = state.get("registry", {}).get("system.health", "UNKNOWN")
                print(f"  Status: {health}")
                print(f"  Last Stabilizer Check: {last_check}")
        else:
            print("  State file not found.")

    def check_task_progress(self):
        print("\n--- TASK PROGRESS ---")
        if os.path.exists(self.hub_file):
            with open(self.hub_file, "r") as f:
                tasks = json.load(f)
                pending = len([t for t in tasks if t["status"] == "PENDING"])
                completed = len([t for t in tasks if t["status"] == "COMPLETED"])
                failed = len([t for t in tasks if t["status"] == "FAILED"])
                print(f"  Pending: {pending} | Completed: {completed} | Failed: {failed}")
        else:
            print("  Task hub not found.")

    def run_monitor(self, interval=300):
        while True:
            self.check_kaggle_status()
            self.check_manifold_health()
            self.check_task_progress()
            print("-" * 40)
            time.sleep(interval)

if __name__ == "__main__":
    kernels = [
        "hichambedrani/fso-production-p1-ingestor",
        "hichambedrani/fso-production-p2-executor",
        "hichambedrani/fso-production-p3-stabilizer"
    ]
    monitor = FSOMonitor(kernels)
    # Check once for script output verification
    monitor.check_kaggle_status()
    monitor.check_manifold_health()
    monitor.check_task_progress()
