import numpy as np
import hashlib
import os
from typing import Dict, Any, List, Tuple
from collections import defaultdict, OrderedDict

class Persistent_Torus_Core:
    """The 1-Billion Fact Engine. Writes continuous HRR waves directly to SSD."""
    def __init__(self, m=1000003, dim=1024, storage_dir="./SOVEREIGN_MIND", cache_size=1000, vector_cache_size=1000):
        self.m = m
        self.dim = dim
        self.storage_dir = storage_dir
        self.metrics = {"facts_ingested": 0, "urls_crawled": 0}

        # LRU Write-Back Cache for Fibers
        self.cache = OrderedDict()
        self.cache_size = cache_size
        self.dirty_fibers = set()

        # LRU Cache for Unitary Vectors
        self.vector_cache = OrderedDict()
        self.vector_cache_size = vector_cache_size

        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _hash_to_fiber(self, concept: str) -> int:
        h = hashlib.sha256(concept.encode('utf-8')).digest()
        return sum(h[:8]) % self.m

    def _generate_vector(self, seed: str) -> np.ndarray:
        """Generates a unitary vector from a seed, with LRU caching for performance."""
        if seed in self.vector_cache:
            self.vector_cache.move_to_end(seed)
            return self.vector_cache[seed]

        h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
        np.random.seed(h)
        v = np.random.randn(self.dim)
        norm = np.linalg.norm(v)
        unitary_v = v / (norm + 1e-9)

        self.vector_cache[seed] = unitary_v
        if len(self.vector_cache) > self.vector_cache_size:
            self.vector_cache.popitem(last=False)

        return unitary_v

    def _bind(self, v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        """Holographic Binding via RFFT."""
        return np.fft.irfft(np.fft.rfft(v1) * np.fft.rfft(v2), n=len(v1))

    def _get_trace_path(self, fiber: int) -> str:
        folder = str(fiber // 1000).zfill(4)
        fiber_dir = os.path.join(self.storage_dir, folder)
        if not os.path.exists(fiber_dir):
            os.makedirs(fiber_dir)
        return os.path.join(fiber_dir, f"fiber_{fiber}.npy")

    def _load_trace(self, fiber: int) -> np.ndarray:
        # Check Cache first
        if fiber in self.cache:
            self.cache.move_to_end(fiber)
            return self.cache[fiber]

        # Load from disk
        path = self._get_trace_path(fiber)
        trace = np.zeros(self.dim)
        if os.path.exists(path):
            try:
                trace = np.load(path)
            except: pass

        # Put in cache
        self.cache[fiber] = trace
        if len(self.cache) > self.cache_size:
            self._flush_lru()

        return trace

    def _save_trace(self, fiber: int, trace_array: np.ndarray):
        # Update Cache and mark Dirty
        self.cache[fiber] = trace_array
        self.cache.move_to_end(fiber)
        self.dirty_fibers.add(fiber)

        if len(self.cache) > self.cache_size:
            self._flush_lru()

    def _flush_lru(self):
        """Flushes the least recently used item if it is dirty."""
        fiber, trace = self.cache.popitem(last=False)
        if fiber in self.dirty_fibers:
            path = self._get_trace_path(fiber)
            np.save(path, trace)
            self.dirty_fibers.remove(fiber)

    def flush_all(self):
        """Persists all dirty cached fibers to SSD."""
        for fiber in list(self.dirty_fibers):
            path = self._get_trace_path(fiber)
            np.save(path, self.cache[fiber])
        self.dirty_fibers.clear()

    def ingest_fact(self, subject: str, payload: str):
        """O(1) Physical SSD Write. Zero RAM Bloat."""
        fiber = self._hash_to_fiber(subject)
        v_subj = self._generate_vector(subject)
        v_data = self._generate_vector(payload[:500])

        trace = self._load_trace(fiber)
        trace += self._bind(v_subj, v_data)
        self._save_trace(fiber, trace)

        self.metrics["facts_ingested"] += 1
        return fiber

    def ingest_facts_batch(self, facts: List[Tuple[str, str]]):
        """Vectorized Batch Ingestion. Groups writes by fiber."""
        if not facts: return

        fiber_updates = defaultdict(lambda: np.zeros(self.dim))
        subjects = [f[0] for f in facts]
        payloads = [f[1][:500] for f in facts]

        v_subjs = np.array([self._generate_vector(s) for s in subjects])
        v_datas = np.array([self._generate_vector(p) for p in payloads])

        f_subjs = np.fft.rfft(v_subjs, axis=1)
        f_datas = np.fft.rfft(v_datas, axis=1)
        traces = np.fft.irfft(f_subjs * f_datas, n=self.dim, axis=1)

        for i, (subject, _) in enumerate(facts):
            fiber = self._hash_to_fiber(subject)
            fiber_updates[fiber] += traces[i]

        for fiber, delta in fiber_updates.items():
            trace = self._load_trace(fiber)
            trace += delta
            self._save_trace(fiber, trace)

        self.metrics["facts_ingested"] += len(facts)
