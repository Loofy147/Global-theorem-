import numpy as np
import time

dim = 4096
num_vectors = 1500
registry = [np.random.randn(dim) for _ in range(num_vectors)]
registry = [v / np.linalg.norm(v) for v in registry]
noisy_vector = np.random.randn(dim)
noisy_vector /= np.linalg.norm(noisy_vector)

def cleanup_original(noisy_vector, registry, threshold=0.3):
    best_sim = -1
    best_vec = None
    for clean_v in registry:
        sim = np.dot(noisy_vector, clean_v)
        if sim > best_sim:
            best_sim = sim
            best_vec = clean_v
    if best_sim >= threshold:
        return best_vec
    return noisy_vector

matrix = np.array(registry)

def cleanup_vectorized(noisy_vector, matrix, threshold=0.3):
    sims = np.dot(matrix, noisy_vector)
    idx = np.argmax(sims)
    if sims[idx] >= threshold:
        return matrix[idx]
    return noisy_vector

# Benchmark
n = 100
start = time.time()
for _ in range(n):
    cleanup_original(noisy_vector, registry)
end = time.time()
print(f"Original cleanup: {end - start:.4f}s")

start = time.time()
for _ in range(n):
    cleanup_vectorized(noisy_vector, matrix)
end = time.time()
print(f"Vectorized cleanup: {end - start:.4f}s")
