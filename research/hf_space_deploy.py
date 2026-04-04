import os
from huggingface_hub import HfApi

def deploy():
    api = HfApi()
    token = os.getenv("HF_TOKEN")
    if not token:
        print("[!] HF_TOKEN not found in environment.")
        return

    # User is LOOFYYLO, not Loofy147 on HF
    repo_id = "LOOFYYLO/FSO-Genesis-Space"

    print(f"[*] Deploying to {repo_id}...")
    try:
        api.create_repo(repo_id=repo_id, token=token, repo_type="space", space_sdk="docker", exist_ok=True)
        api.upload_folder(
            folder_path=".",
            repo_id=repo_id,
            repo_type="space",
            token=token,
            ignore_patterns=[".git*", "__pycache__*", "*.log", "*.parquet", "kaggle_data*"]
        )
        print("[+] Deployment successful.")
    except Exception as e:
        print(f"[!] Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
