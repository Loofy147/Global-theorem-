import subprocess
import os
import json
import random

# Problems to target
CONFIGS = [
    {"prob": "P1", "m": 4, "k": 4, "engine": "fiber", "seeds": range(10, 20)},
    {"prob": "P2", "m": 6, "k": 3, "engine": "hybrid", "seeds": range(10, 15)},
    {"prob": "P3", "m": 8, "k": 3, "engine": "hybrid", "seeds": range(10, 15)},
]

def deploy():
    token = "KGAT_453cfb028676f79df571e5b2a8ee6afd"
    username = "hichambedrani"
    os.environ["KAGGLE_API_TOKEN"] = token
    os.environ["KAGGLE_USERNAME"] = username

    # Use the self-contained script from p1/kaggle_search.py
    with open("p1/kaggle_search.py", "r") as f:
        base_code = f.read()

    for cfg in CONFIGS:
        prob = cfg["prob"]
        m, k, engine = cfg["m"], cfg["k"], cfg["engine"]

        for seed in cfg["seeds"]:
            kernel_id = f"claudes-cycles-{prob.lower()}-v31-massive-s{seed}"
            dir_name = f"massive_{prob}_{seed}"
            os.makedirs(dir_name, exist_ok=True)

            code = base_code
            code = code.replace('seed = random.randint(0, 1000000)', f'seed = {seed}')
            code = code.replace('problem = os.environ.get("KAGGLE_PROBLEM", "P3")', f'problem = "{prob}"')
            code = code.replace('m = int(os.environ.get("KAGGLE_M", 8))', f'm = {m}')
            code = code.replace('k = int(os.environ.get("KAGGLE_K", 3))', f'k = {k}')
            code = code.replace('engine = os.environ.get("KAGGLE_ENGINE", "hybrid")', f'engine = "{engine}"')
            code = code.replace('iters = int(os.environ.get("MAX_ITER", 30_000_000))', 'iters = 50_000_000')

            with open(f"{dir_name}/kaggle_search.py", "w") as f:
                f.write(code)

            metadata = {
                "id": f"{username}/{kernel_id}",
                "title": kernel_id,
                "code_file": "kaggle_search.py",
                "language": "python",
                "kernel_type": "script",
                "is_private": "true",
                "enable_gpu": "false",
                "enable_internet": "false",
                "dataset_sources": [],
                "competition_sources": [],
                "kernel_sources": [],
                "model_sources": []
            }

            with open(f"{dir_name}/kernel-metadata.json", "w") as f:
                json.dump(metadata, f)

            print(f"Deploying {kernel_id}...")
            subprocess.run(["kaggle", "kernels", "push", "-p", dir_name])

if __name__ == "__main__":
    deploy()
