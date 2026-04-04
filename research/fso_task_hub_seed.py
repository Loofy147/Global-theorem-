import sys
import os
# Add paths
sys.path.insert(0, os.path.join(os.getcwd(), "research"))
sys.path.insert(0, os.getcwd())

from fso_task_hub import FSOTaskHub

def seed():
    hub = FSOTaskHub(m=31)

    # 1. Transformers Sentiment Analysis
    hub.add_task("transformers.pipeline", {
        "task": "sentiment-analysis",
        "model": "distilbert-base-uncased-finetuned-sst-2-english"
    }, priority=10)

    # 2. Dataset Loading
    hub.add_task("datasets.load_dataset", {
        "path": "rotten_tomatoes",
        "split": "train[:10]"
    }, priority=8)

    # 3. Scientific Computing
    hub.add_task("numpy.mean", {"a": [1, 2, 3, 4, 5]}, priority=5)
    hub.add_task("torch.add", {"input": [10, 20], "other": [30, 40]}, priority=5)

    # 4. Project Internal Logic (Topological Call)
    hub.add_task("project.core.solve", {}, priority=12)
    hub.add_task("project.theorems.verify_all_theorems", {}, priority=15)

    hub.save_hub()
    print(f"[*] Seeded task hub with {len(hub.tasks)} tasks.")

if __name__ == "__main__":
    seed()
