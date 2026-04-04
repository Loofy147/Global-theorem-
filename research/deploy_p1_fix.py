import os
import subprocess

def deploy_fix():
    token = os.environ.get("KAGGLE_API_TOKEN")
    if not token:
        print("[!] KAGGLE_API_TOKEN not set.")
        return

    print(f"[*] Deploying p1 fix using token: {token[:5]}...")
    metadata = "kernel-metadata-p1.json"
    if os.path.exists(metadata):
        os.rename(metadata, "kernel-metadata.json")
        subprocess.run(["kaggle", "kernels", "push", "-p", "."], check=True)
        os.rename("kernel-metadata.json", metadata)
        print("[+] p1 fix pushed.")

if __name__ == "__main__":
    deploy_fix()
