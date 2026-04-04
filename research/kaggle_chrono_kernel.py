import asyncio
import os
import json
import base64
import time
import logging
import requests
from datetime import datetime

# Configure logging
logger = logging.getLogger("KAGGL_KERNEL")

class KaggleFSOWrapper:
    """
    Wraps the FSO Apex Hypervisor for the 12-hour Kaggle GPU lifecycle.
    Manages GitHub State I/O via REST API to make the Manifold 'Immortal'.
    """
    def __init__(self, repo_url: str, m: int = 31):
        # Extract owner and repo from URL: https://github.com/owner/repo.git
        parts = repo_url.replace(".git", "").split("/")
        self.repo_owner = parts[-2]
        self.repo_name = parts[-1]
        self.m = m
        self.state_file = "fso_manifold_state.json"
        self.github_token = os.getenv("GITHUB_PAT")
        self.global_registry = {}
        self.api_base = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents"

    def pull_memory(self):
        """Pulls the previous generation's topological map from GitHub REST API."""
        logger.info(f"Synchronizing Manifold Memory from GitHub API: {self.repo_owner}/{self.repo_name}...")

        if not self.github_token:
            logger.warning("No GITHUB_PAT found. Attempting local load...")
            if os.path.exists(self.state_file):
                try:
                    with open(self.state_file, "r") as f:
                        state = json.load(f)
                        self.global_registry = state.get("registry", {})
                        logger.info(f"Loaded {len(self.global_registry)} Anchored Logic Gates from local file.")
                except Exception as e:
                    logger.error(f"Error loading local state: {e}")
            return

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.get(f"{self.api_base}/{self.state_file}", headers=headers)
            if response.status_code == 200:
                content = response.json()
                file_content = base64.b64decode(content['content']).decode('utf-8')
                state = json.loads(file_content)
                self.global_registry = state.get("registry", {})
                logger.info(f"Successfully pulled {len(self.global_registry)} logic gates from GitHub.")
            else:
                logger.warning(f"Failed to pull state from API (Status: {response.status_code}). Check if file exists.")
        except Exception as e:
            logger.error(f"API Pull Error: {e}")

    def push_memory(self):
        """Saves the evolved topological map and pushes back to GitHub via REST API."""
        logger.info("Committing Manifold State via GitHub API...")

        state = {
            "timestamp": datetime.now().isoformat(),
            "m_size": self.m,
            "registry": self.global_registry
        }

        # Also save locally
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=4)

        if not self.github_token:
            logger.warning("No GITHUB_PAT found. Skipping API push.")
            return

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            # 1. Get current SHA
            sha = None
            response = requests.get(f"{self.api_base}/{self.state_file}", headers=headers)
            if response.status_code == 200:
                sha = response.json().get('sha')

            # 2. Update/Create file
            content_str = json.dumps(state, indent=4)
            encoded_content = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')

            data = {
                "message": f"Autopoietic Evolution: {state['timestamp']}",
                "content": encoded_content
            }
            if sha:
                data["sha"] = sha

            put_res = requests.put(f"{self.api_base}/{self.state_file}", headers=headers, json=data)
            if put_res.status_code in [200, 201]:
                logger.info("State successfully anchored to GitHub via API.")
            else:
                logger.error(f"Failed to push state (Status: {put_res.status_code}): {put_res.text}")
        except Exception as e:
            logger.error(f"API Push Error: {e}")

async def kaggle_lifecycle():
    repo = os.getenv("FSO_REPO_URL", "https://github.com/hichambedrani/Global-theorem-.git")
    runner = KaggleFSOWrapper(repo_url=repo)
    runner.pull_memory()
    duration = float(os.getenv("FSO_CYCLE_DURATION", "0.01"))

    # Simple simulated loop for standalone testing
    end_time = time.time() + (duration * 3600)
    while time.time() < end_time:
        await asyncio.sleep(1)
        if os.getenv("FSO_DEMO_MODE"): break

    runner.push_memory()

if __name__ == "__main__":
    asyncio.run(kaggle_lifecycle())
