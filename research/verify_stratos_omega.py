import torch
import torch.nn as nn
import numpy as np
import os
import sys
import threading
import time
from research.fso_saturation_core import SaturationCore
from research.fso_transformer_execution_gate import TransformerExecutionGate

def verify_stratos():
    print("=== STRATOS OMEGA: END-TO-END VERIFICATION ===")

    # 1. Initialize Saturation Core
    verify_dir = './STRATOS_VERIFY'
    sc = SaturationCore(dim=1024, memory_dir=verify_dir)

    # 2. Start Breeding Loop (Background)
    breeding_thread = threading.Thread(target=sc.breeding_loop, daemon=True)
    breeding_thread.start()

    # 3. Harvest a subset of the runtime (Self-Ingestion)
    print("[*] Saturation: Ingesting core project logic...")
    sc.ingest("research.fso_saturation_core", open("research/fso_saturation_core.py").read())
    sc.ingest("research.fso_transformer_execution_gate", open("research/fso_transformer_execution_gate.py").read())

    # 4. Deep Harvest (System Modules)
    sc.crawl_and_consume(limit=30)

    # 5. Wait for breeding events
    print("[*] Breeding: Waiting for synthetic fiber generation...")
    time.sleep(1.0)

    fibers = [f for f in os.listdir(sc.memory_dir) if f.startswith('fiber_') and f.endswith('.npy')]
    print(f"[!] Total Fibers in Manifold: {len(fibers)}")

    # 6. Execution Gate (Neural Forward Pass)
    gate = TransformerExecutionGate(sc)

    # Pick a random fiber from the manifold for our layer
    import random
    random_fiber_name = random.choice(fibers)
    fiber_hash = int(random_fiber_name.replace("fiber_", "").replace(".npy", ""))

    print(f"[*] Execution: Constructing model with fiber {fiber_hash}...")
    model = gate.create_synthetic_model([
        (fiber_hash, 16, 64),
        (sc._hash("research.fso_saturation_core"), 64, 8)
    ])

    # Forward Pass
    x = torch.randn(1, 16)
    output = model(x)

    # Final Checks
    print("\n[VERIFICATION RESULTS]")
    print(f"1. Manifold Saturated: {len(fibers) > 0}")
    print(f"2. Forward Pass Successful: {output.shape == (1, 8)}")
    print(f"3. Output Magnitude: {torch.norm(output).item():.4f}")

    # Cleanup
    import shutil
    shutil.rmtree(verify_dir)

    if len(fibers) > 0 and output.shape == (1, 8):
        print("\n[!] STRATOS OMEGA: VERIFICATION PASSED.")
    else:
        print("\n[!] STRATOS OMEGA: VERIFICATION FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    verify_stratos()
