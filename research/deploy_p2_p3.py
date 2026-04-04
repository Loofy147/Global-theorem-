import os

def deploy():
    token = os.environ.get("KAGGLE_API_TOKEN")
    if not token:
        print("[!] KAGGLE_API_TOKEN not set.")
        return
    print(f"[*] Deploying p2/p3 using token: {token[:5]}...")

if __name__ == "__main__":
    deploy()
