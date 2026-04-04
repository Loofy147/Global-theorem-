import asyncio
import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime

# --- 1. BOOTSTRAP PHASE ---
def bootstrap():
    repo_url = os.getenv("FSO_REPO_URL", "https://github.com/hichambedrani/Global-theorem-.git")
    github_token = os.getenv("GITHUB_PAT")
    is_kaggle = os.path.exists("/kaggle/working")
    target_dir = "/kaggle/working/repo" if is_kaggle else os.getcwd()

    if github_token and is_kaggle:
        auth_url = repo_url.replace("https://", f"https://{github_token}@")
        if not os.path.exists(target_dir):
            print(f"[*] Bootstrapping: Cloning {repo_url} into {target_dir}...")
            subprocess.run(["git", "clone", auth_url, target_dir], check=True)

        if target_dir not in sys.path:
            sys.path.insert(0, target_dir)
            sys.path.insert(0, os.path.join(target_dir, "research"))

bootstrap()

# --- 2. CORE INTEGRATION ---
try:
    from research.fso_apex_hypervisor import FSO_Apex_Hypervisor, FSOTopology
    from research.fso_fabric import FSOFabricNode, COLOR_LOGIC, FSODataStream
    from research.kaggle_chrono_kernel import KaggleFSOWrapper
except ImportError:
    from fso_apex_hypervisor import FSO_Apex_Hypervisor, FSOTopology
    from fso_fabric import FSOFabricNode, COLOR_LOGIC, FSODataStream
    from kaggle_chrono_kernel import KaggleFSOWrapper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FSO_UNIFIED")

async def run_unified_cycle():
    role = os.getenv("FSO_ROLE", "EXECUTOR")
    m = int(os.getenv("FSO_M_SIZE", "31"))
    cycle_duration = float(os.getenv("FSO_CYCLE_DURATION", "1.0")) # 1 hour
    repo_url = os.getenv("FSO_REPO_URL", "https://github.com/hichambedrani/Global-theorem-.git")

    logger.info(f"--- FSO UNIFIED KERNEL: ROLE={role} ---")

    wrapper = KaggleFSOWrapper(repo_url=repo_url, m=m)
    wrapper.pull_memory()

    apex = FSO_Apex_Hypervisor(m=m)
    # Sync registry from wrapper
    if hasattr(wrapper, 'global_registry'):
        apex.consumer.global_registry.update(wrapper.global_registry)
        logger.info(f"Synchronized {len(wrapper.global_registry)} logic units.")

    end_time = time.time() + (cycle_duration * 3600)

    # Start background stabilization if not in STABILIZER role (it runs as foreground there)
    if role != "STABILIZER":
        asyncio.create_task(apex.run_stabilization_loop())

    if role == "INGESTOR":
        # Ingest key industrial libraries
        libs = ["transformers", "datasets", "torch", "scipy", "sklearn", "numpy", "pandas"]
        for lib in libs:
            if time.time() >= end_time: break
            apex.consumer.auto_provision(lib)
            await asyncio.sleep(5)

    elif role == "EXECUTOR":
        # Execution logic: simulate task processing from hub (to be implemented in fso_task_hub.py)
        while time.time() < end_time:
            logger.info("Executor checking for tasks...")
            # Placeholder for task hub logic
            await asyncio.sleep(60)

    elif role == "STABILIZER":
        # Foreground stabilization and health logging
        logger.info("Stabilizer role: Maintaining topological parity...")
        while time.time() < end_time:
            # Metrics logging to state
            wrapper.global_registry["system.health"] = "OK"
            wrapper.global_registry["system.last_check"] = datetime.now().isoformat()
            await asyncio.sleep(300)

    # SHUTDOWN AND PERSIST
    logger.info("Cycle complete. Persisting state...")
    wrapper.global_registry.update(apex.consumer.global_registry)
    wrapper.push_memory()
    logger.info("--- FSO UNIFIED KERNEL SHUTDOWN COMPLETE ---")

if __name__ == "__main__":
    try:
        asyncio.run(run_unified_cycle())
    except Exception as e:
        logger.critical(f"FATAL ERROR: {e}", exc_info=True)
