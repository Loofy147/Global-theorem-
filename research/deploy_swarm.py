import os
import subprocess
import shutil

def deploy_production_swarm():
    # Credentials from environment (passed by Jules)
    kaggle_username = "hichambedrani"
    kaggle_token = os.environ.get("KAGGLE_API_TOKEN") # KGAT_...
    github_pat = os.environ.get("GITHUB_PAT")

    if not kaggle_token:
        print("[!] KAGGLE_API_TOKEN not set in environment.")
        return

    # Setup Kaggle credentials for CLI
    home = os.path.expanduser("~")
    os.makedirs(os.path.join(home, ".kaggle"), exist_ok=True)
    with open(os.path.join(home, ".kaggle", "kaggle.json"), "w") as f:
        import json
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
            # We copy to kernel-metadata.json for the CLI to pick up (unless we use -p)
            # Actually kaggle kernels push -p . uses kernel-metadata.json in that folder.
            # So we swap them.
            shutil.copy(metadata, "kernel-metadata.json")
            try:
                subprocess.run(["kaggle", "kernels", "push", "-p", "."], check=True)
                print(f"[+] {metadata} pushed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"[!] Failed to push {metadata}: {e}")
        else:
            print(f"[!] {metadata} not found.")

    # Cleanup
    if os.path.exists("kernel-metadata.json"):
        os.remove("kernel-metadata.json")

if __name__ == "__main__":
    deploy_production_swarm()
