import os
import subprocess

def deploy():
    token = os.environ.get("KAGGLE_API_TOKEN")
    if not token:
        print("[!] KAGGLE_API_TOKEN not set.")
        return

    print(f"[*] Deploying p2/p3 using token: {token[:5]}...")
    # Add real logic to push p2 and p3 kernels
    # Assuming appropriate metadata files exist for these
    for metadata in ["kernel-metadata-p2.json", "kernel-metadata-p3.json"]:
        if os.path.exists(metadata):
            # Temporarily rename to standard filename for kaggle cli
            os.rename(metadata, "kernel-metadata.json")
            subprocess.run(["kaggle", "kernels", "push", "-p", "."], check=True)
            os.rename("kernel-metadata.json", metadata)
            print(f"[+] {metadata} pushed.")

if __name__ == "__main__":
    deploy()
