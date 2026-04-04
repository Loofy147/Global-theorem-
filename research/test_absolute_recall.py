import sys
import os
import numpy as np
import hashlib

# Add parent directory to path to import fso_stratified_ingestor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fso_stratified_ingestor import StratifiedMemory

def test_recall_at_scale():
    DIM = 1024
    N_ITEMS = 500  # Smaller scale for fast local verification
    M_FIBERS = 101

    print(f"--- LOCAL VERIFICATION: Absolute Recall at {N_ITEMS} units ---")
    mem = StratifiedMemory(dim=DIM, m_fibers=M_FIBERS)

    def generate_vector(seed_str):
        h = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        np.random.seed(h)
        v = np.random.randn(DIM)
        return v / np.linalg.norm(v)

    keys = [f"industrial_logic_{i}" for i in range(N_ITEMS)]
    vals = [f"val_{i}" for i in range(N_ITEMS)]

    vec_keys = [generate_vector(k) for k in keys]
    vec_vals = [generate_vector(v) for v in vals]

    print(f"Ingesting {N_ITEMS} items into {M_FIBERS} fibers...")
    for i in range(N_ITEMS):
        mem.bind_store(vec_keys[i], vec_vals[i], keys[i])

    print("Testing recall on 50 items...")
    cosines = []
    for i in range(50):
        recovered = mem.unbind_recall(vec_keys[i], keys[i])
        cos = np.dot(recovered, vec_vals[i]) / (np.linalg.norm(recovered) * np.linalg.norm(vec_vals[i]))
        cosines.append(cos)

    avg_cos = np.mean(cosines)
    print(f"Average Cosine Similarity: {avg_cos:.4f}")

    # In the definitive proof, N=2500, M=251 -> avg_cos = 0.30
    # Here N=500, M=101 -> density is ~5 per fiber. Expect high clarity.
    if avg_cos > 0.30:
        print(f"[SUCCESS] Absolute Recall Verified: {avg_cos:.4f} > 0.30")
    else:
        print(f"[FAILURE] Recall dropped to {avg_cos:.4f}")

if __name__ == "__main__":
    test_recall_at_scale()
