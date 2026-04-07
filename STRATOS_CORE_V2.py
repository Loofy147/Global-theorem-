import os
import sys
import subprocess
import importlib
import inspect
import numpy as np
import shutil
import hashlib
import fcntl

class StratosEngineV2:
    def __init__(self, dim=4096, memory_dir='./STRATOS_MEMORY_V2'):
        self.dim = dim
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)
        self.identity_map = {}

    def _generate_unitary_vector(self, seed):
        state = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(state)
        return np.random.normal(0, 1/np.sqrt(self.dim), self.dim)

    def bind(self, a, b):
        return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real

    def unbind(self, composite, a):
        return np.fft.ifft(np.conj(np.fft.fft(a)) * np.fft.fft(composite)).real

    def _get_semantic_signature(self, obj):
        try:
            return inspect.getsource(obj)
        except:
            try:
                return str(obj.__code__.co_code) if hasattr(obj, '__code__') else str(obj)
            except:
                return str(obj)

    def _atomic_add(self, filepath, vector):
        mode = 'rb+' if os.path.exists(filepath) else 'wb+'
        with open(filepath, mode) as f:
            if mode == 'rb+':
                fcntl.flock(f, fcntl.LOCK_EX)
                existing = np.load(f)
                if existing.shape != vector.shape:
                    # Dimension correction: replace if old memory is incompatible
                    new_v = vector
                else:
                    new_v = existing + vector
                f.seek(0)
                np.save(f, new_v)
                f.truncate()
                fcntl.flock(f, fcntl.LOCK_UN)
            else:
                np.save(f, vector)

    def ingest_semantic(self, path_name, obj):
        sig = self._get_semantic_signature(obj)
        v_id = self._generate_unitary_vector(path_name)
        v_content = self._generate_unitary_vector(sig)
        trace = self.bind(v_id, v_content)
        bucket = path_name.split('.')[0]
        file_path = os.path.join(self.memory_dir, f"bucket_{bucket}.npy")
        self._atomic_add(file_path, trace)

    def query(self, path_name):
        bucket = path_name.split('.')[0]
        file_path = os.path.join(self.memory_dir, f"bucket_{bucket}.npy")
        if not os.path.exists(file_path):
            return None
        v_id = self._generate_unitary_vector(path_name)
        with open(file_path, 'rb') as f:
            manifold_segment = np.load(f)
        if manifold_segment.shape != v_id.shape:
            return None
        return self.unbind(manifold_segment, v_id)

