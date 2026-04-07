import os
import sys
import subprocess
import importlib
import inspect
import numpy as np
import shutil
import hashlib
import fcntl

class TopologicalCleanUpGate:
    """
    Stabilizes the Torus by snapping noisy vectors to the nearest clean unitary anchor.
    Prevents Catastrophic Semantic Collapse by stripping crosstalk.
    """
    def __init__(self, dim=1024):
        self.dim = dim
        self.item_memory = {} # label -> clean_vector
        self.vector_registry = [] # list of (vector, label)

    def register(self, label, vector):
        norm = np.linalg.norm(vector)
        clean_v = vector / norm if norm > 1e-9 else vector
        self.item_memory[label] = clean_v
        self.vector_registry.append((clean_v, label))

    def cleanup(self, noisy_vector, threshold=0.3):
        if not self.vector_registry:
            return noisy_vector

        norm = np.linalg.norm(noisy_vector)
        v_norm = noisy_vector / norm if norm > 1e-9 else noisy_vector

        best_sim = -1
        best_vec = None

        for clean_v, label in self.vector_registry:
            sim = np.dot(v_norm, clean_v)
            if sim > best_sim:
                best_sim = sim
                best_vec = clean_v

        if best_sim >= threshold:
            return best_vec
        return noisy_vector

class StratosEngineV2:
    def __init__(self, dim=4096, memory_dir='./STRATOS_MEMORY_V2'):
        self.dim = dim
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)
        self.cleanup_gate = TopologicalCleanUpGate(dim=dim)

    def _generate_unitary_vector(self, seed):
        state = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(state)
        v = np.random.normal(0, 1/np.sqrt(self.dim), self.dim)
        # Force unit length for TGI Field Equations compatibility
        norm = np.linalg.norm(v)
        return v / norm if norm > 1e-9 else v

    def bind(self, a, b):
        """Holographic Binding: Circular Convolution (a * b)"""
        return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real

    def unbind(self, composite, a):
        """Holographic Unbinding: Circular Correlation (composite # a)"""
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
                try:
                    existing = np.load(f)
                    if existing.shape != vector.shape:
                        new_v = vector
                    else:
                        new_v = existing + vector
                    f.seek(0)
                    np.save(f, new_v)
                    f.truncate()
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            else:
                np.save(f, vector)

    def ingest_semantic(self, path_name, obj):
        sig = self._get_semantic_signature(obj)
        v_id = self._generate_unitary_vector(path_name)
        v_content = self._generate_unitary_vector(sig)

        # Register in Clean-up gate
        self.cleanup_gate.register(path_name, v_id)
        self.cleanup_gate.register(f"sig:{path_name}", v_content)

        trace = self.bind(v_id, v_content)
        bucket = path_name.split('.')[0]
        file_path = os.path.join(self.memory_dir, f"bucket_{bucket}.npy")
        self._atomic_add(file_path, trace)

    def query(self, path_name, use_cleanup=True):
        bucket = path_name.split('.')[0]
        file_path = os.path.join(self.memory_dir, f"bucket_{bucket}.npy")
        if not os.path.exists(file_path):
            return None
        v_id = self._generate_unitary_vector(path_name)
        with open(file_path, 'rb') as f:
            manifold_segment = np.load(f)
        if manifold_segment.shape != v_id.shape:
            return None

        retrieved = self.unbind(manifold_segment, v_id)
        if use_cleanup:
            return self.cleanup_gate.cleanup(retrieved)
        return retrieved

