import os

def deploy_fix():
    token = os.environ.get("KAGGLE_API_TOKEN")
    if not token:
        print("[!] KAGGLE_API_TOKEN not set.")
        return
    print(f"[*] Deploying p1 fix using token: {token[:5]}...")

if __name__ == "__main__":
    deploy_fix()
