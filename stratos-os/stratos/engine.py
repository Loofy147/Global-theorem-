import numpy as np
import hashlib
import os
import json
import logging
import fcntl
from collections import OrderedDict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("STRATOS_V2")

class StratosEngineV2:
    def __init__(self, dim=4096, memory_dir="STRATOS_MEMORY_V2", vector_cache_size=1000):
        self.dim = dim
        self.memory_dir = memory_dir
        if not os.path.exists(memory_dir):
            os.makedirs(memory_dir)
        self.vector_cache = OrderedDict() # Cache for (vector, rfft_vector)
        self.vector_cache_size = vector_cache_size

    def _generate_unitary_vector(self, seed: str, return_rfft=False):
        """Generates a unitary vector from a seed, with LRU caching for performance."""
        if seed in self.vector_cache:
            self.vector_cache.move_to_end(seed)
            v, f_v = self.vector_cache[seed]
            return (v, f_v) if return_rfft else v

        np.random.seed(int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**32))
        phase = np.random.uniform(0, 2 * np.pi, self.dim)
        unitary_v = np.exp(1j * phase)

        # Pre-compute RFFT for caching to accelerate bind/unbind operations
        # Note: Using complex FFT as this engine implementation uses complex vectors
        f_v = np.fft.fft(unitary_v)

        self.vector_cache[seed] = (unitary_v, f_v)
        if len(self.vector_cache) > self.vector_cache_size:
            self.vector_cache.popitem(last=False)

        return (unitary_v, f_v) if return_rfft else unitary_v

    def bind(self, a, b):
        return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b))

    def unbind(self, composite, a, fft_a=None):
        f_a = fft_a if fft_a is not None else np.fft.fft(a)
        return np.fft.ifft(np.fft.fft(composite) / f_a)

    def ingest_semantic(self, path_name: str, obj_logic: str):
        logger.info(f"Ingesting semantic logic for '{path_name}'...")
        v_path = self._generate_unitary_vector(path_name)
        v_logic = self._generate_unitary_vector(obj_logic)
        v_combined = self.bind(v_path, v_logic)

        bucket_name = path_name.split('.')[0] if '.' in path_name else 'misc'
        filepath = os.path.join(self.memory_dir, f"bucket_{bucket_name}.npy")
        self._atomic_add(filepath, v_combined)

    def _atomic_add(self, filepath, vector):
        if os.path.exists(filepath):
            with open(filepath, 'rb+') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                existing = np.load(f)
                np.save(f, existing + vector)
                fcntl.flock(f, fcntl.LOCK_UN)
        else:
            with open(filepath, 'wb') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                np.save(f, vector)
                fcntl.flock(f, fcntl.LOCK_UN)

    def query(self, path_name: str):
        # Use cached vector and its pre-computed FFT to optimize unbinding
        v_path, f_path = self._generate_unitary_vector(path_name, return_rfft=True)
        bucket_name = path_name.split('.')[0] if '.' in path_name else 'misc'
        filepath = os.path.join(self.memory_dir, f"bucket_{bucket_name}.npy")

        if not os.path.exists(filepath):
            return None

        with open(filepath, 'rb') as f:
            manifold_vector = np.load(f)

        # Pass pre-computed FFT to unbind for speed
        v_retrieved = self.unbind(manifold_vector, v_path, fft_a=f_path)
        return v_retrieved
