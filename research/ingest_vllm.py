import os
import json
import sys
from typing import List, Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from fso_refinery import FSORefinery

def ingest_vllm_logic(repo_path: str, m_val: int = 31):
    print(f"[*] Starting vLLM Logic Ingestion (m={m_val})...")
    refinery = FSORefinery(m_val)

    # Target core directories for high-performance inference distribution
    target_dirs = [
        os.path.join(repo_path, "vllm", "model_executor"),
        os.path.join(repo_path, "vllm", "distributed"),
        os.path.join(repo_path, "vllm", "engine")
    ]

    all_units = []
    for d in target_dirs:
        if os.path.exists(d):
            print(f"  [+] Smelting directory: {d}")
            all_units.extend(refinery.refinery_process(d))

    # Filter for "Advanced Specifications" (High-impact logic)
    # Focus on attention, paged_attention, distributed, scheduling, kernels
    keywords = ["attention", "paged", "dist", "broadcast", "all_reduce", "schedule", "kernel"]
    filtered_units = [u for u in all_units if any(kw in u['id'].lower() for kw in keywords)]

    print(f"[*] Extracted {len(all_units)} total units. Filtered to {len(filtered_units)} high-impact units.")

    # Save to vault
    vault_path = os.path.join(os.path.dirname(__file__), "fso_vllm_logic_vault.py")
    with open(vault_path, "w") as f:
        f.write("# FSO vLLM Logic Vault\n")
        f.write("# Ingested Atomic Logic Units for the Neural Industry\n\n")
        f.write("VLLM_LOGIC_UNITS = " + json.dumps(filtered_units, indent=4) + "\n")

    print(f"[!] Successfully anchored {len(filtered_units)} units to {vault_path}")

if __name__ == "__main__":
    vllm_path = "/tmp/vllm_repo"
    if os.path.exists(vllm_path):
        ingest_vllm_logic(vllm_path)
    else:
        print(f"[ERROR] vLLM repo not found at {vllm_path}")
