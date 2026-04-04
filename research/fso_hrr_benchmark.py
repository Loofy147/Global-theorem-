import numpy as np
import hashlib
import time

def generate_vector(dim=1024, seed_str=""):
    """Generate a stable, normalized random vector."""
    # Use deterministic seeding for reproducible benchmarks
    seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    np.random.seed(seed_val)
    v = np.random.randn(dim)
    return v / np.linalg.norm(v)

def bind(v1, v2):
    """Circular convolution via FFT."""
    return np.fft.ifft(np.fft.fft(v1) * np.fft.fft(v2)).real

def unbind(bound_v, v1):
    """
    Retrieval via FFT and the Complex Conjugate requirement.
    (Theorem 4.2 from the FSO Algebraic Codex)
    """
    return np.fft.ifft(np.fft.fft(bound_v) * np.conj(np.fft.fft(v1))).real

def cosine_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)

def run_benchmark():
    DIM = 1024
    N_ITEMS = 2500  # Number of key-value pairs to store
    M_FIBERS = 251  # Prime modulus for FSO

    print(f"--- BENCHMARK: STANDARD HRR vs FSO-STRATIFIED HRR ---")
    print(f"Dimensions: {DIM} | Items to store: {N_ITEMS} | FSO Fibers: {M_FIBERS}")

    # 1. Generate Dataset
    print("Generating dataset...")
    keys = [f"Key_{i}" for i in range(N_ITEMS)]
    vals = [f"Val_{i}" for i in range(N_ITEMS)]

    vec_keys = [generate_vector(DIM, k) for k in keys]
    vec_vals = [generate_vector(DIM, v) for v in vals]

    # ==========================================
    # TEST 1: Standard HRR (Single Global Trace)
    # ==========================================
    print("\n[Test 1] Running Standard HRR...")
    start_t = time.time()
    standard_trace = np.zeros(DIM)

    for i in range(N_ITEMS):
        standard_trace += bind(vec_keys[i], vec_vals[i])

    write_time_std = time.time() - start_t

    # Retrieval Test (Sample 100 items)
    start_t = time.time()
    std_cosines = []
    for i in range(100):
        recovered = unbind(standard_trace, vec_keys[i])
        std_cosines.append(cosine_sim(recovered, vec_vals[i]))
    read_time_std = time.time() - start_t

    avg_std_cos = np.mean(std_cosines)

    # ==========================================
    # TEST 2: FSO-Stratified HRR (m=251 Traces)
    # ==========================================
    print("[Test 2] Running FSO-Stratified HRR...")
    start_t = time.time()

    fso_traces = {f: np.zeros(DIM) for f in range(M_FIBERS)}

    for i in range(N_ITEMS):
        # Closure Lemma / Fiber Hashing (O(1) operation)
        h = hashlib.sha256(keys[i].encode()).digest()
        # Simplified fiber routing: modulo addition mapping to 1 of 251 fibers
        fiber = sum(h[:3]) % M_FIBERS

        fso_traces[fiber] += bind(vec_keys[i], vec_vals[i])

    write_time_fso = time.time() - start_t

    # Retrieval Test (Same 100 items)
    start_t = time.time()
    fso_cosines = []
    for i in range(100):
        h = hashlib.sha256(keys[i].encode()).digest()
        fiber = sum(h[:3]) % M_FIBERS

        recovered = unbind(fso_traces[fiber], vec_keys[i])
        fso_cosines.append(cosine_sim(recovered, vec_vals[i]))
    read_time_fso = time.time() - start_t

    avg_fso_cos = np.mean(fso_cosines)

    # ==========================================
    # RESULTS
    # ==========================================
    print("\n--- RESULTS ---")
    print(f"Standard HRR Average Cosine Similarity: {avg_std_cos:.4f}")
    print(f"FSO-HRR      Average Cosine Similarity: {avg_fso_cos:.4f}")
    print(f"Signal Clarity Multiplier: {avg_fso_cos / max(avg_std_cos, 0.0001):.2f}x better")
    print("\n--- PERFORMANCE OVERHEAD ---")
    print(f"Standard Write: {write_time_std:.4f}s | Read (100): {read_time_std:.4f}s")
    print(f"FSO Write:      {write_time_fso:.4f}s | Read (100): {read_time_fso:.4f}s")

if __name__ == "__main__":
    run_benchmark()
