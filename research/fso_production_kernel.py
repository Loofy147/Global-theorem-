import asyncio
import os
import json
import subprocess
import time
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Tuple, List

# --- BOOTSTRAP PHASE ---
def bootstrap():
    # Use the current remote URL if available, else fallback
    try:
        remote_url = subprocess.check_output(["git", "remote", "get-url", "origin"]).decode().strip()
    except:
        remote_url = os.getenv("FSO_REPO_URL", "https://github.com/Loofy147/Global-theorem-.git")
    
    github_token = os.getenv("GITHUB_PAT")
    is_kaggle = os.path.exists("/kaggle/working")
    target_dir = "/kaggle/working/repo" if is_kaggle else os.path.join(os.getcwd(), "test_repo")
    
    if github_token:
        # Construct authenticated URL
        if "github.com" in remote_url and github_token not in remote_url:
            auth_url = remote_url.replace("https://", f"https://{github_token}@")
        else:
            auth_url = remote_url
            
        if not os.path.exists(target_dir):
            print(f"[*] Bootstrapping: Cloning {remote_url} into {target_dir}...")
            try:
                subprocess.run(["git", "clone", auth_url, target_dir], check=True)
            except Exception as e:
                print(f"[!] Clone failed: {e}. Proceeding with local files.")
        
        if os.path.exists(target_dir):
            if target_dir not in sys.path:
                sys.path.insert(0, target_dir)
                sys.path.insert(0, os.path.join(target_dir, "research"))

bootstrap()

# --- PROJECT IMPORTS ---
try:
    from research.fso_apex_hypervisor import FSO_Apex_Hypervisor
    from research.fso_evolution_engine import FSO_Evolution_Engine, TopologicalGravity
    from research.kaggle_chrono_kernel import KaggleFSOWrapper
except ImportError:
    try:
        from fso_apex_hypervisor import FSO_Apex_Hypervisor
        from fso_evolution_engine import FSO_Evolution_Engine, TopologicalGravity
        from kaggle_chrono_kernel import KaggleFSOWrapper
    except ImportError:
        sys.path.append(os.getcwd())
        sys.path.append(os.path.join(os.getcwd(), "research"))
        from fso_apex_hypervisor import FSO_Apex_Hypervisor
        from fso_evolution_engine import FSO_Evolution_Engine, TopologicalGravity
        from kaggle_chrono_kernel import KaggleFSOWrapper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PRODUCTION_KERNEL")

async def run_production_loop():
    logger.info("--- FSO PRODUCTION KERNEL STARTING ---")
    m = int(os.getenv("FSO_M_SIZE", "31"))
    
    # Get Repo URL for wrapper
    try:
        repo_url = subprocess.check_output(["git", "remote", "get-url", "origin"]).decode().strip()
    except:
        repo_url = "https://github.com/Loofy147/Global-theorem-.git"
        
    cycle_duration = float(os.getenv("FSO_CYCLE_DURATION", "11.5"))
    
    apex = FSO_Apex_Hypervisor(m=m)
    engine = FSO_Evolution_Engine(apex)
    wrapper = KaggleFSOWrapper(repo_url=repo_url, m=m)
    
    wrapper.pull_memory()
    converted_registry = {}
    for k, v in wrapper.global_registry.items():
        if isinstance(k, str) and k.startswith('(') and k.endswith(')'):
            try:
                coords = eval(k)
                converted_registry[coords] = v
            except: pass
    
    apex.consumer.global_registry.update(converted_registry)
    logger.info(f"Synchronized {len(converted_registry)} logic anchors.")

    asyncio.create_task(apex.run_stabilization_loop())
    
    end_time = time.time() + (cycle_duration * 3600)
    logger.info(f"Initiating production cycle for {cycle_duration} hours.")
    
    while time.time() < end_time:
        try:
            # DRIVE EVOLUTION
            await engine.evaluate_and_evolve("math.sqrt", (0,0,0), 144)
        except Exception as e:
            logger.error(f"Error: {e}")
            
        await asyncio.sleep(600 if not os.getenv("FSO_DEMO_MODE") else 1)
        if os.getenv("FSO_DEMO_MODE"): break
            
    logger.info("Production cycle ending.")
    wrapper.global_registry = {str(k): v for k, v in apex.consumer.global_registry.items()}
    wrapper.push_memory()
    logger.info("--- FSO PRODUCTION KERNEL SHUTDOWN COMPLETE ---")

if __name__ == "__main__":
    try:
        asyncio.run(run_production_loop())
    except Exception as e:
        logger.critical(f"FATAL: {e}", exc_info=True)
