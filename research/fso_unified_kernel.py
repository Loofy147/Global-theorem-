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
    # Fix sys.path for Kaggle and Local
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))

    if current_dir not in sys.path: sys.path.insert(0, current_dir)
    if project_root not in sys.path: sys.path.insert(0, project_root)

    # Repository details
    repo_url = os.getenv("FSO_REPO_URL", "https://github.com/hichambedrani/Global-theorem-.git")
    github_token = os.getenv("GITHUB_PAT")
    is_kaggle = os.path.exists("/kaggle/working")
    target_dir = "/kaggle/working/repo" if is_kaggle else project_root

    # Pathing: Ensure research is discoverable
    if is_kaggle and target_dir not in sys.path:
        sys.path.insert(0, target_dir)
        sys.path.insert(0, os.path.join(target_dir, "research"))

bootstrap()

# --- 2. CORE INTEGRATION ---
try:
    from fso_apex_hypervisor import FSO_Apex_Hypervisor, FSOTopology
    from fso_fabric import FSOFabricNode, COLOR_LOGIC, FSODataStream
    from kaggle_chrono_kernel import KaggleFSOWrapper
    from fso_task_hub import FSOTaskHub
except ImportError:
    try:
        from research.fso_apex_hypervisor import FSO_Apex_Hypervisor, FSOTopology
        from research.fso_fabric import FSOFabricNode, COLOR_LOGIC, FSODataStream
        from research.kaggle_chrono_kernel import KaggleFSOWrapper
        from research.fso_task_hub import FSOTaskHub
    except ImportError:
        # Monolithic Fallback for Kaggle
        sys.path.append(os.getcwd())
        from fso_apex_hypervisor import FSO_Apex_Hypervisor, FSOTopology
        from fso_fabric import FSOFabricNode, COLOR_LOGIC, FSODataStream
        from kaggle_chrono_kernel import KaggleFSOWrapper
        from fso_task_hub import FSOTaskHub

# Configure logging to both file and stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fso_runtime.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("FSO_UNIFIED")

async def run_unified_cycle():
    # ROLE and CONFIG
    role = os.getenv("FSO_ROLE", "EXECUTOR")
    m = int(os.getenv("FSO_M_SIZE", "31"))
    cycle_duration = float(os.getenv("FSO_CYCLE_DURATION", "1.0")) # 1 hour
    repo_url = os.getenv("FSO_REPO_URL", "https://github.com/hichambedrani/Global-theorem-.git")

    logger.info(f"--- FSO UNIFIED KERNEL: ROLE={role} ---")

    # 1. Initialize API Wrapper & Hub
    wrapper = KaggleFSOWrapper(repo_url=repo_url, m=m)
    wrapper.pull_memory() # API Sync

    apex = FSO_Apex_Hypervisor(m=m)
    task_hub = FSOTaskHub(m=m)

    # 2. Synchronize logic from memory
    if hasattr(wrapper, 'global_registry'):
        apex.consumer.global_registry.update(wrapper.global_registry)
        logger.info(f"Synchronized {len(wrapper.global_registry)} logic units.")

    end_time = time.time() + (cycle_duration * 3600)

    # Start background stabilization for all roles
    asyncio.create_task(apex.run_stabilization_loop())

    if role == "INGESTOR":
        logger.info("Ingestor role: Provisioning industrial libraries...")
        libs = ["transformers", "datasets", "torch", "scipy", "sklearn", "numpy", "pandas"]
        for lib in libs:
            if time.time() >= end_time: break
            apex.consumer.auto_provision(lib)
            await asyncio.sleep(5)
            # Notify task hub of new ingestion
            task_hub.add_task(f"{lib}.__name__", {}, priority=1)

    elif role == "EXECUTOR":
        logger.info("Executor role: Processing task waveforms...")
        while time.time() < end_time:
            pending_tasks = task_hub.get_pending_tasks(role)
            for task in pending_tasks:
                logger.info(f"Intersection: Processing Task {task['id']} at {task['target']}")
                # Execute via Hypervisor
                result = await apex.command_execution(task['logic_id'], **task['params'])
                task_hub.complete_task(task['id'], result)
                logger.info(f"Task {task['id']} Result: {str(result)[:100]}...")

            await asyncio.sleep(60) # Interval for task polling

    elif role == "STABILIZER":
        logger.info("Stabilizer role: Maintaining manifold integrity...")
        while time.time() < end_time:
            # 1. Log health
            wrapper.global_registry["system.health"] = "OK"
            wrapper.global_registry["system.last_check"] = datetime.now().isoformat()

            # 2. Cleanup task hub
            task_hub.cleanup_stale_tasks(timeout_seconds=1800)

            # 3. Snapshot and push intermediate state periodically (every 10 mins)
            if int(time.time()) % 600 < 60:
                logger.info("Stabilizer Snapshot: Pushing intermediate state...")
                wrapper.global_registry.update({str(k): v for k, v in apex.consumer.global_registry.items()})
                wrapper.push_memory()

            await asyncio.sleep(60)

    # 3. SHUTDOWN AND FINAL PERSIST
    logger.info("Cycle complete. Performing final state synchronization...")
    wrapper.global_registry.update({str(k): v for k, v in apex.consumer.global_registry.items()})
    wrapper.push_memory()

    # Kaggle output persistence
    if os.path.exists("/kaggle/working"):
        subprocess.run(["cp", "fso_runtime.log", "/kaggle/working/"])

    logger.info("--- FSO UNIFIED KERNEL SHUTDOWN COMPLETE ---")

if __name__ == "__main__":
    try:
        # Handle already running loops in some environments
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_unified_cycle())
    except Exception as e:
        logger.critical(f"FATAL ERROR: {e}", exc_info=True)
