import os
import subprocess
import shutil
import json

def deploy_production_swarm():
    # Credentials from Jules
    kaggle_username = "hichambedrani"
    kaggle_token = os.getenv("KAGGLE_API_TOKEN")
    github_pat = os.getenv("GITHUB_PAT")

    # Setup Kaggle credentials
    home = os.path.expanduser("~")
    os.makedirs(os.path.join(home, ".kaggle"), exist_ok=True)
    with open(os.path.join(home, ".kaggle", "kaggle.json"), "w") as f:
        json.dump({"username": kaggle_username, "key": kaggle_token}, f)
    os.chmod(os.path.join(home, ".kaggle", "kaggle.json"), 0o600)

    # Production Metadata files
    production_kernels = [
        "kernel-metadata-production-p1.json",
        "kernel-metadata-production-p2.json",
        "kernel-metadata-production-p3.json"
    ]

    for metadata in production_kernels:
        if os.path.exists(metadata):
            print(f"[*] Deploying {metadata}...")
            shutil.copy(metadata, "kernel-metadata.json")
            try:
                # push everything in root (.)
                subprocess.run(["kaggle", "kernels", "push", "-p", "."], check=True)
                print(f"[+] {metadata} pushed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"[!] Failed to push {metadata}: {e}")
        else:
            print(f"[!] {metadata} not found.")

if __name__ == "__main__":
    deploy_production_swarm()
