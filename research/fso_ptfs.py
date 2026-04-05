import numpy as np
import hashlib
import os
from typing import Dict, Any

class Persistent_Torus_Core:
    """The 1-Billion Fact Engine. Writes continuous HRR waves directly to SSD."""
    def __init__(self, m=1000003, dim=1024, storage_dir="./SOVEREIGN_MIND"):
        self.m = m
        self.dim = dim
        self.storage_dir = storage_dir
        self.metrics = {"facts_ingested": 0, "urls_crawled": 0}

        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _hash_to_fiber(self, concept: str) -> int:
        h = hashlib.sha256(concept.encode('utf-8')).digest()
        return sum(h[:8]) % self.m

    def _generate_vector(self, seed: str) -> np.ndarray:
        h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
        np.random.seed(h)
        v = np.random.randn(self.dim)
        return v / np.linalg.norm(v)

    def _bind(self, v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        return np.fft.ifft(np.fft.fft(v1) * np.fft.fft(v2)).real

    def _get_trace_path(self, fiber: int) -> str:
        folder = str(fiber // 1000).zfill(4)
        fiber_dir = os.path.join(self.storage_dir, folder)
        if not os.path.exists(fiber_dir):
            os.makedirs(fiber_dir)
        return os.path.join(fiber_dir, f"fiber_{fiber}.npy")

    def _load_trace(self, fiber: int) -> np.ndarray:
        path = self._get_trace_path(fiber)
        if os.path.exists(path):
            try:
                return np.load(path)
            except: pass
        return np.zeros(self.dim)

    def _save_trace(self, fiber: int, trace_array: np.ndarray):
        path = self._get_trace_path(fiber)
        np.save(path, trace_array)

    def ingest_fact(self, subject: str, payload: str):
        """O(1) Physical SSD Write. Zero RAM Bloat."""
        fiber = self._hash_to_fiber(subject)
        v_subj = self._generate_vector(subject)
        v_data = self._generate_vector(payload[:500]) # Cap to 500 chars for clean HRR wave

        trace = self._load_trace(fiber)
        trace += self._bind(v_subj, v_data)
        self._save_trace(fiber, trace)

        self.metrics["facts_ingested"] += 1
        return fiber
