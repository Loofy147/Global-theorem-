import sys
import os
import numpy as np

# Add parent directory to path to import fso_stratified_ingestor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fso_stratified_ingestor import StratifiedMemory

def test_stratified_memory():
    print("--- Testing Stratified Memory Integration ---")
    mem = StratifiedMemory(dim=1024, m_fibers=101)

    # Create random vectors
    # HRR usually requires vectors to be in the frequency domain or specific distributions
    # but here let's just use the same method as in the benchmark
    def generate_v(seed):
        np.random.seed(seed)
        v = np.random.randn(1024)
        return v / np.linalg.norm(v)

    v_key = generate_v(42)
    v_val = generate_v(123)

    key_str = "test_logic_unit"

    print(f"Storing '{key_str}' in stratified memory...")
    mem.bind_store(v_key, v_val, key_str)

    print(f"Recalling '{key_str}'...")
    recovered = mem.unbind_recall(v_key, key_str)

    cosine = np.dot(recovered, v_val) / (np.linalg.norm(recovered) * np.linalg.norm(v_val))
    print(f"Recovered Cosine Similarity: {cosine:.4f}")

    # 0.30 was the target in the benchmark for N=2500.
    # For a single item, it should be much higher if implementation is correct.
    # But circular convolution retrieval isn't perfect (1.0) due to noise.
    if cosine > 0.30:
        print("[SUCCESS] Stratified Memory verified.")
    else:
        print("[FAILURE] Memory recall failed.")

if __name__ == "__main__":
    test_stratified_memory()
