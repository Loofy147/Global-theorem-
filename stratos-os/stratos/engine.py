import numpy as np
import hashlib
import os
import json
import logging
import fcntl

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("STRATOS_V2")

class StratosEngineV2:
    def __init__(self, dim=4096, memory_dir="STRATOS_MEMORY_V2"):
        self.dim = dim
        self.memory_dir = memory_dir
        if not os.path.exists(memory_dir):
            os.makedirs(memory_dir)

    def _generate_unitary_vector(self, seed: str):
        np.random.seed(int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**32))
        phase = np.random.uniform(0, 2 * np.pi, self.dim)
        return np.exp(1j * phase)

    def bind(self, a, b):
        return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b))

    def unbind(self, composite, a):
        return np.fft.ifft(np.fft.fft(composite) / np.fft.fft(a))

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
        v_path = self._generate_unitary_vector(path_name)
        bucket_name = path_name.split('.')[0] if '.' in path_name else 'misc'
        filepath = os.path.join(self.memory_dir, f"bucket_{bucket_name}.npy")

        if not os.path.exists(filepath):
            return None

        with open(filepath, 'rb') as f:
            manifold_vector = np.load(f)

        v_retrieved = self.unbind(manifold_vector, v_path)
        return v_retrieved
