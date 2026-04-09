import numpy as np
import time
import os

dim = 4096
n_files = 100
os.makedirs("test_mmap", exist_ok=True)

# Create files
for i in range(n_files):
    np.save(f"test_mmap/f_{i}.npy", np.random.randn(dim))

# Benchmark standard load
start = time.perf_counter()
for i in range(n_files):
    v = np.load(f"test_mmap/f_{i}.npy")
    v += 1.0
    np.save(f"test_mmap/f_{i}.npy", v)
end = time.perf_counter()
print(f"Standard load/save: {end - start:.4f}s")

# Benchmark mmap load
start = time.perf_counter()
for i in range(n_files):
    v = np.load(f"test_mmap/f_{i}.npy", mmap_mode='r+')
    v += 1.0
    # No need to np.save if we modified in place, but r+ mmap needs to be handled carefully
    v.flush()
end = time.perf_counter()
print(f"Mmap load/flush: {end - start:.4f}s")

import shutil
shutil.rmtree("test_mmap")
