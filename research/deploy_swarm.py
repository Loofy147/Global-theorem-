import subprocess
import os
import json
import random

PROBLEMS = [
    {"name": "p1", "m": 4, "k": 4, "engine": "fiber", "seeds": [42, 123, 789, 101112]},
    {"name": "p2", "m": 6, "k": 3, "engine": "hybrid", "seeds": [42, 123, 789, 101112]}
]

def deploy():
    # Use environment for token if available, otherwise fallback to provided string
    # This ensures portability while keeping defaults for the user.
    token = os.environ.get("KAGGLE_API_TOKEN", "KGAT_453cfb028676f79df571e5b2a8ee6afd")
    username = os.environ.get("KAGGLE_USERNAME", "hichambedrani")

    os.environ["KAGGLE_API_TOKEN"] = token
    os.environ["KAGGLE_USERNAME"] = username

    for prob in PROBLEMS:
        base_name = prob["name"]
        m, k = prob["m"], prob["k"]
        engine = prob["engine"]

        for seed in prob["seeds"]:
            kernel_id = f"claudes-cycles-{base_name}-v31-s{seed}"
            dir_name = f"swarm_{base_name}_{seed}"
            os.makedirs(dir_name, exist_ok=True)

            # Use the latest kaggle_search.py logic
            # This logic should be updated in the repository to include v3.1 moves.
            try:
                with open("p1/kaggle_search.py", "r") as f:
                    code = f.read()
            except FileNotFoundError:
                print("Warning: p1/kaggle_search.py not found. Please ensure it is synced.")
                continue

            code = code.replace('seed = random.randint(0, 1000000)', f'seed = {seed}')
            code = code.replace('problem = os.environ.get("KAGGLE_PROBLEM", "P3")', f'problem = "{base_name.upper()}"')
            code = code.replace('m = int(os.environ.get("KAGGLE_M", 8))', f'm = {m}')
            code = code.replace('k = int(os.environ.get("KAGGLE_K", 3))', f'k = {k}')
            code = code.replace('engine = os.environ.get("KAGGLE_ENGINE", "hybrid")', f'engine = "{engine}"')

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

            print(f"Deploying swarm kernel: {kernel_id}...")
            subprocess.run(["kaggle", "kernels", "push", "-p", dir_name])
            print("  (Dry run: kaggle kernels push -p " + dir_name + ")")

if __name__ == "__main__":
    deploy()
