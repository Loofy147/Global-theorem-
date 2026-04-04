import sys
import os
import numpy as np
import hashlib
import json

# Add parent directory to path to import fso_stratified_ingestor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fso_stratified_ingestor import StratifiedMemory, FSOTopology, DirectConsumer

def test_full_ingestor_flow():
    print("--- STARTING EXTENDED INGESTOR VERIFICATION ---")

    # 1. Topology & Coordinate Check
    m = 101
    topo = FSOTopology(m)
    coords = topo.get_coords("numpy.mean")
    print(f"Coords for 'numpy.mean': {coords}")
    assert len(coords) == 3
    assert all(0 <= c < m for c in coords)

    # 2. Memory Recall Verification
    mem = StratifiedMemory(dim=1024, m_fibers=m)
    def gen_vec(s):
        h = int(hashlib.md5(s.encode()).hexdigest()[:8], 16)
        np.random.seed(h)
        v = np.random.randn(1024)
        return v / np.linalg.norm(v)

    k_vec = gen_vec("test_key")
    v_vec = gen_vec("test_val")
    mem.bind_store(k_vec, v_vec, "test_key")
    rec = mem.unbind_recall(k_vec, "test_key")
    cos = np.dot(rec, v_vec) / (np.linalg.norm(rec) * np.linalg.norm(v_vec))
    print(f"Recall Cosine: {cos:.4f}")
    assert cos > 0.6

    # 3. Direct Consumer Check (mocking numpy)
    consumer = DirectConsumer(topo)
    # Check if builtins work
    print("Testing execute on builtins.len...")
    res = consumer.execute("len", obj=[1,2,3])
    print(f"len([1,2,3]) = {res}")
    assert res == 3

    print("[SUCCESS] Extended Ingestor Verification Passed.")

if __name__ == "__main__":
    test_full_ingestor_flow()
