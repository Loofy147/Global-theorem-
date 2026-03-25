import subprocess
import os
import json

def deploy():
    token = "KGAT_453cfb028676f79df571e5b2a8ee6afd"
    username = "hichambedrani"
    os.environ["KAGGLE_API_TOKEN"] = token
    os.environ["KAGGLE_USERNAME"] = username

    with open("p1/kaggle_search.py", "r") as f:
        code = f.read()

    prob = "P1"
    m, k, engine = 4, 4, "fiber"
    seed = 12

    kernel_id = f"claudes-cycles-p1-v31-fixed-s{seed}"
    dir_name = f"fixed_p1_{seed}"
    os.makedirs(dir_name, exist_ok=True)

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
            {"key": "MAX_ITER", "value": "50000000"},
            {"key": "SEED", "value": str(seed)}
        ]
    }

    with open(f"{dir_name}/kernel-metadata.json", "w") as f:
        json.dump(metadata, f)

    print(f"Deploying {kernel_id}...")
    subprocess.run(["kaggle", "kernels", "push", "-p", dir_name])

if __name__ == "__main__":
    deploy()
