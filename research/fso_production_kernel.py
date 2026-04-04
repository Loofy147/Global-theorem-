import asyncio
import os
import json
import subprocess
import time
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, List

# Add parent directory to path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research.fso_apex_hypervisor import FSO_Apex_Hypervisor
from research.fso_evolution_engine import FSO_Evolution_Engine, TopologicalGravity
from research.kaggle_chrono_kernel import KaggleFSOWrapper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PRODUCTION_KERNEL")

async def run_production_loop():
    logger.info("--- FSO PRODUCTION KERNEL STARTING ---")

    # Configuration
    m = int(os.getenv("FSO_M_SIZE", "31"))
    repo_url = os.getenv("FSO_REPO_URL", "https://github.com/hichambedrani/FSO-Manifold.git")
    cycle_duration = float(os.getenv("FSO_CYCLE_DURATION", "11.5")) # Hours

    # 1. Initialize Components
    apex = FSO_Apex_Hypervisor(m=m)
    engine = FSO_Evolution_Engine(apex)
    wrapper = KaggleFSOWrapper(repo_url=repo_url, m=m)

    # 2. Bootstrapping (Pull Memory)
    wrapper.pull_memory()
    # Synchronize wrapper registry to hypervisor consumer
    # Convert string keys back to tuples if they look like coordinates
    converted_registry = {}
    for k, v in wrapper.global_registry.items():
        if isinstance(k, str) and k.startswith('(') and k.endswith(')'):
            try:
                coords = eval(k)
                converted_registry[coords] = v
            except:
                logger.error(f"Failed to parse coordinate string: {k}")
        else:
            # If it's a direct logic_id -> coords mapping in wrapper, handle that too
            pass

    apex.consumer.global_registry.update(converted_registry)
    logger.info(f"Synchronized {len(converted_registry)} logic anchors from storage.")

    # 3. Start Stabilization
    asyncio.create_task(apex.run_stabilization_loop())

    # 4. Main Evolutionary Loop
    end_time = time.time() + (cycle_duration * 3600)
    logger.info(f"Initiating production cycle for {cycle_duration} hours.")

    # Example Production Task: Mass Ingestion of Core Stack
    initial_libraries = ["numpy", "scipy", "torch", "sklearn", "pandas", "matplotlib"]
    for lib in initial_libraries:
        apex.consumer.auto_provision(lib)

    while time.time() < end_time:
        # Perform autonomous tasks, evaluation, and evolution
        # Simulate some workload for evolution to happen
        try:
            # Execute some logic from math or numpy
            await engine.evaluate_and_evolve("numpy.fft.fft", (0,0,0), [1, 2, 3])
            await engine.evaluate_and_evolve("numpy.linalg.inv", (5,5,5), [[1, 2], [3, 4]])
        except Exception as e:
            logger.error(f"Error in background execution task: {e}")

        await asyncio.sleep(600) # Check every 10 minutes

        time_remaining = (end_time - time.time()) / 3600
        logger.info(f"Manifold healthy. Time remaining: {time_remaining:.2f} hours.")

        # Break if in demo mode
        if os.getenv("FSO_DEMO_MODE"):
            logger.info("Demo mode: breaking early.")
            break

    # 5. Shutdown and Push Memory
    logger.info("Production cycle ending. Preparing state anchor...")
    # Update wrapper registry from hypervisor consumer (stringifying keys for JSON)
    wrapper.global_registry = {str(k): v for k, v in apex.consumer.global_registry.items()}
    wrapper.push_memory()

    logger.info("--- FSO PRODUCTION KERNEL SHUTDOWN COMPLETE ---")

if __name__ == "__main__":
    try:
        asyncio.run(run_production_loop())
    except KeyboardInterrupt:
        logger.info("Manual termination received.")
    except Exception as e:
        logger.critical(f"FATAL ERROR in production kernel: {e}")
