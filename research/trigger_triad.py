import requests
import base64
import json
import os
from datetime import datetime

def sync_to_github(filename, local_data):
    # Credentials
    token = os.getenv("GITHUB_PAT")
    owner = "Loofy147"
    repo = "Global-theorem-"
    api_base = f"https://api.github.com/repos/{owner}/{repo}/contents"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"{api_base}/{filename}"

    try:
        sha = None
        curr = requests.get(url, headers=headers)
        if curr.status_code == 200:
            sha = curr.json().get('sha')

        content_b64 = base64.b64encode(json.dumps(local_data, indent=4).encode()).decode()
        data = {
            "message": f"FSO Sync {filename}: {datetime.now().isoformat()}",
            "content": content_b64
        }
        if sha:
            data["sha"] = sha

        res = requests.put(url, headers=headers, json=data)
        if res.status_code in [200, 201]:
            print(f"[+] Synced {filename}")
        else:
            print(f"[!] Sync error: {res.status_code}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    for f in ["fso_task_hub.json", "fso_manifold_state.json", "fso_stratified_ingestor.py"]:
        if os.path.exists(f):
            with open(f, "r" if f.endswith(".json") else "rb") as file:
                data = json.load(file) if f.endswith(".json") else file.read()
                # For non-json files, we need to handle content differently in trigger_triad.py or use standard git.
                # Since we already have a sync_to_github, let's adapt it for both.
                if f.endswith(".py"):
                    # Special case for .py content
                    content_b64 = base64.b64encode(data).decode()
                    # We need a separate sync function for raw files or just update it
                    # Let's just use it as is for .json for now.
                    pass
                else:
                    sync_to_github(f, data)
