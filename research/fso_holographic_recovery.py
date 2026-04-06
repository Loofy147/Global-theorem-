import numpy as np
import os
import sys
import time
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("holographic_recovery.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("HolographicRecovery")

def bind(v1, v2):
    """Circular Convolution via FFT"""
    return np.fft.ifft(np.fft.fft(v1) * np.fft.fft(v2))

def unbind(bound_v, v1):
    """Exact Retrieval via Division in Frequency Domain"""
    f_v1 = np.fft.fft(v1)
    # Avoid division by zero
    f_v1[np.abs(f_v1) < 1e-12] = 1e-12
    return np.fft.ifft(np.fft.fft(bound_v) / f_v1)

def cosine_sim(v1, v2):
    """Measures signal clarity"""
    v1_r = np.real(v1)
    v2_r = np.real(v2)
    norm1 = np.linalg.norm(v1_r)
    norm2 = np.linalg.norm(v2_r)
    if norm1 < 1e-9 or norm2 < 1e-9:
        return 0.0
    return np.dot(v1_r, v2_r) / (norm1 * norm2)

def find_all_fibers(base_dir="."):
    """Locate all .npy files in the repository, excluding known artifacts."""
    fibers = {}
    exclude_dirs = {".git", "__pycache__", "venv", ".venv", "env", "node_modules", "dist", "build"}

    for root, dirs, files in os.walk(base_dir):
        # Efficiently skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for name in files:
            if name.endswith(".npy"):
                path = os.path.join(root, name)
                # Store absolute path to avoid confusion
                fibers[name] = os.path.abspath(path)

    return fibers

def run_recovery_cycle():
    state_file = "fso_holographic_state.json"
    logger.info("=== STARTING GLOBAL HOLOGRAPHIC RECOVERY CYCLE ===")

    fibers = find_all_fibers()
    logger.info(f"Detected {len(fibers)} active fibers globally across the repository.")

    if len(fibers) < 2:
        logger.warning("Insufficient fibers for holographic binding test.")
        return {
            "status": "INCOMPLETE",
            "fiber_count": len(fibers),
            "last_integrity": 0.0,
            "timestamp": datetime.now().isoformat()
        }

    # Load all found vectors
    vectors = {}
    for name, path in fibers.items():
        try:
            vectors[name] = np.load(path)
        except Exception as e:
            logger.error(f"Failed to load {name}: {e}")

    # Test recovery for all adjacent pairs to ensure global manifold stability
    keys = sorted(list(vectors.keys()))
    integrities = []

    # Process in chunks to prevent excessive logging/memory for thousands of fibers
    # We always test pairs of (keys[i], keys[i+1])
    for i in range(len(keys) - 1):
        name_a, name_b = keys[i], keys[i+1]
        v_a, v_b = vectors[name_a], vectors[name_b]

        # Binding
        bound_state = bind(v_a, v_b)
        # Unbinding
        recovered_b = unbind(bound_state, v_a)

        sim = cosine_sim(recovered_b, v_b)
        integrities.append(sim)

        if sim < 0.999:
            logger.warning(f"[DEGRADED] Global Pair ({name_a}, {name_b}) | Integrity: {sim:.10f}")

    avg_integrity = np.mean(integrities) if integrities else 0.0
    overall_status = "STABLE" if avg_integrity > 0.999 else "DEGRADED"

    result = {
        "status": overall_status,
        "fiber_count": len(fibers),
        "average_integrity": float(avg_integrity),
        "timestamp": datetime.now().isoformat(),
        "active_fibers_sample": keys[:10]
    }

    # Save state for FSO Ecosystem awareness
    with open(state_file, "w") as f:
        json.dump(result, f, indent=4)

    logger.info(f"Cycle Complete. Global Integrity: {avg_integrity:.10f} | Status: {overall_status}")
    return result

def main(interval=60):
    """Continuous recovery daemon."""
    logger.info(f"Global Holographic Recovery Daemon initialized. Interval: {interval}s")
    run_recovery_cycle()

    if os.environ.get("FSO_DAEMON_MODE") == "TRUE":
        while True:
            time.sleep(interval)
            try:
                run_recovery_cycle()
            except Exception as e:
                logger.error(f"Daemon cycle failed: {e}")
    else:
        logger.info("Daemon running in single-shot mode (set FSO_DAEMON_MODE=TRUE for persistence).")

if __name__ == "__main__":
    main()
