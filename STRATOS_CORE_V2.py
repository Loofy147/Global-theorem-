import os
import sys
import subprocess
import importlib
import inspect
import numpy as np
import shutil
import hashlib
import fcntl
from collections import defaultdict, OrderedDict

class TopologicalCleanUpGate:
    """
    Stabilizes the Torus by snapping noisy vectors to the nearest clean unitary anchor.
    Prevents Catastrophic Semantic Collapse by stripping crosstalk.
    """
    def __init__(self, dim=1024):
        self.dim = dim
        self.item_memory = {} # label -> clean_vector
        self.vector_registry = [] # list of (vector, label)
        self.vector_matrix = None # Matrix for vectorized cleanup

    def register(self, label, vector):
        norm = np.linalg.norm(vector)
        clean_v = vector / (norm + 1e-9)
        self.item_memory[label] = clean_v
        self.vector_registry.append((clean_v, label))
        self.vector_matrix = None # Invalidate matrix cache

    def batch_register(self, label_vector_pairs):
        """Register multiple vectors at once to minimize matrix invalidations."""
        for label, vector in label_vector_pairs:
            norm = np.linalg.norm(vector)
            clean_v = vector / (norm + 1e-9)
            self.item_memory[label] = clean_v
            self.vector_registry.append((clean_v, label))
        self.vector_matrix = None

    def cleanup(self, noisy_vector, threshold=0.3):
        if not self.vector_registry:
            return noisy_vector

        if self.vector_matrix is None:
            # Rebuild matrix cache for vectorized operations
            self.vector_matrix = np.array([v for v, label in self.vector_registry])

        norm = np.linalg.norm(noisy_vector)
        if norm < 1e-9: return noisy_vector
        v_norm = noisy_vector / norm

        # Vectorized similarity calculation: O(N*D) in BLAS
        sims = np.dot(self.vector_matrix, v_norm)
        best_idx = np.argmax(sims)
        best_sim = sims[best_idx]

        if best_sim >= threshold:
            return self.vector_registry[best_idx][0]
        return noisy_vector

class StratosEngineV2:
    def __init__(self, dim=4096, memory_dir='./STRATOS_MEMORY_V2', cache_size=100):
        self.dim = dim
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)
        self.cleanup_gate = TopologicalCleanUpGate(dim=dim)
        # Use OrderedDict for simple LRU cache
        self.bucket_cache = OrderedDict()
        self.cache_size = cache_size

    def warm_up(self, registry_dict):
        """Pre-registers topological anchors from a global registry for high-fidelity denoising."""
        print(f"[*] STRATOS: Warming up manifold with {len(registry_dict)} anchors...")
        pairs = []
        for path_name, data in registry_dict.items():
            # If registry contains pre-generated vectors, use them.
            # Otherwise, use identity seed to generate.
            if isinstance(data, np.ndarray):
                v_id = data
            elif isinstance(data, dict) and 'id_vector' in data:
                v_id = np.array(data['id_vector'])
            else:
                v_id = self._generate_unitary_vector(path_name)

            pairs.append((path_name, v_id))

        self.cleanup_gate.batch_register(pairs)

    def _generate_unitary_vector(self, seed):
        state = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(state)
        v = np.random.normal(0, 1/np.sqrt(self.dim), self.dim)
        # Force unit length for TGI Field Equations compatibility
        norm = np.linalg.norm(v)
        return v / (norm + 1e-9)

    def bind(self, a, b):
        """Holographic Binding: Circular Convolution via RFFT (optimized for real signals)"""
        return np.fft.irfft(np.fft.rfft(a) * np.fft.rfft(b), n=len(a))

    def unbind(self, composite, a):
        """Holographic Unbinding: Circular Correlation via RFFT (optimized for real signals)"""
        return np.fft.irfft(np.conj(np.fft.rfft(a)) * np.fft.rfft(composite), n=len(composite))

    def _get_semantic_signature(self, obj):
        try:
            return inspect.getsource(obj)
        except:
            try:
                return str(obj.__code__.co_code) if hasattr(obj, '__code__') else str(obj)
            except:
                return str(obj)

    def _update_cache(self, filepath, vector):
        if filepath in self.bucket_cache:
            self.bucket_cache.move_to_end(filepath)
        self.bucket_cache[filepath] = vector
        if len(self.bucket_cache) > self.cache_size:
            self.bucket_cache.popitem(last=False)

    def _atomic_add(self, filepath, vector):
        mode = 'rb+' if os.path.exists(filepath) else 'wb+'
        with open(filepath, mode) as f:
            if mode == 'rb+':
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    existing = np.load(f)
                    new_v = existing + vector
                    f.seek(0)
                    np.save(f, new_v)
                    f.truncate()
                    self._update_cache(filepath, new_v)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            else:
                np.save(f, vector)
                self._update_cache(filepath, vector)

    def ingest_semantic(self, path_name, obj):
        sig = self._get_semantic_signature(obj)
        v_id = self._generate_unitary_vector(path_name)
        v_content = self._generate_unitary_vector(sig)

        # Register in Clean-up gate
        self.cleanup_gate.register(path_name, v_id)
        self.cleanup_gate.register(f"sig:{path_name}", v_content)

        trace = self.bind(v_id, v_content)
        bucket = path_name.split('.')[0]
        file_path = os.path.abspath(os.path.join(self.memory_dir, f"bucket_{bucket}.npy"))
        self._atomic_add(file_path, trace)

    def batch_ingest_semantic(self, item_dict):
        """Ingests multiple items efficiently using vectorized binding and grouped writes."""
        if not item_dict: return

        path_names = list(item_dict.keys())
        sigs = [self._get_semantic_signature(obj) for obj in item_dict.values()]

        # Generate all vectors
        v_ids = np.array([self._generate_unitary_vector(pn) for pn in path_names])
        v_contents = np.array([self._generate_unitary_vector(s) for s in sigs])

        # Vectorized Binding
        f_ids = np.fft.rfft(v_ids, axis=1)
        f_contents = np.fft.rfft(v_contents, axis=1)
        traces = np.fft.irfft(f_ids * f_contents, n=self.dim, axis=1)

        cleanup_pairs = []
        bucket_traces = defaultdict(lambda: np.zeros(self.dim))

        for i, path_name in enumerate(path_names):
            cleanup_pairs.append((path_name, v_ids[i]))
            cleanup_pairs.append((f"sig:{path_name}", v_contents[i]))

            bucket = path_name.split('.')[0]
            bucket_traces[bucket] += traces[i]

        # Batch register all vectors
        self.cleanup_gate.batch_register(cleanup_pairs)

        # Batch write all buckets
        for bucket, trace in bucket_traces.items():
            file_path = os.path.abspath(os.path.join(self.memory_dir, f"bucket_{bucket}.npy"))
            self._atomic_add(file_path, trace)

    def query(self, path_name, use_cleanup=True):
        bucket = path_name.split('.')[0]
        file_path = os.path.abspath(os.path.join(self.memory_dir, f"bucket_{bucket}.npy"))

        if file_path in self.bucket_cache:
            manifold_segment = self.bucket_cache[file_path]
            self.bucket_cache.move_to_end(file_path)
        else:
            if not os.path.exists(file_path):
                return None
            with open(file_path, 'rb') as f:
                manifold_segment = np.load(f)
            self._update_cache(file_path, manifold_segment)

        v_id = self._generate_unitary_vector(path_name)
        if manifold_segment.shape != v_id.shape:
            return None

        retrieved = self.unbind(manifold_segment, v_id)
        if use_cleanup:
            return self.cleanup_gate.cleanup(retrieved)
        return retrieved
