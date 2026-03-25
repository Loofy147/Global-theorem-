import subprocess
import os
import json

CONFIGS = [
    {"prob": "P2", "m": 6, "k": 3, "engine": "hybrid", "seeds": range(20, 25)},
    {"prob": "P3", "m": 8, "k": 3, "engine": "hybrid", "seeds": range(20, 25)},
]

def deploy():
    token = "KGAT_453cfb028676f79df571e5b2a8ee6afd"
    username = "hichambedrani"
    os.environ["KAGGLE_API_TOKEN"] = token
    os.environ["KAGGLE_USERNAME"] = username

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
            code = code.replace('seed = 42', f'seed = {seed}') # Note: check if it matches the current base_code
            # Actually, I should use environment variables in the script or just replace directly.
            # My current kaggle_search.py uses os.environ.get.

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
                "model_sources": [],
                "environment_variables": [
                    {"key": "KAGGLE_PROBLEM", "value": prob},
                    {"key": "KAGGLE_M", "value": str(m)},
                    {"key": "KAGGLE_K", "value": str(k)},
                    {"key": "KAGGLE_ENGINE", "value": engine},
                    {"key": "MAX_ITER", "value": "50000000"}
                ]
            }

            with open(f"{dir_name}/kernel-metadata.json", "w") as f:
                json.dump(metadata, f)

            print(f"Deploying {kernel_id}...")
            subprocess.run(["kaggle", "kernels", "push", "-p", dir_name])

if __name__ == "__main__":
    deploy()
