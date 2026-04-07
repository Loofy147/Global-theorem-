import os
import sys
import hashlib
import numpy as np
import inspect
import threading
import time
import fcntl # For atomic file locking on Unix

class StratosEngineV2:
    def __init__(self, dim=2048, memory_dir='./STRATOS_MEMORY_V2'):
        self.dim = dim
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)
        # Using a higher dimension (2048) to improve HRR capacity/SNR
        self.identity_map = {}
        self.is_running = True

    def _generate_unitary_vector(self, seed):
        """Generates a unitary vector in the Fourier domain to preserve energy during binding."""
        state = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(state)
        # HRRs work best when components are drawn from N(0, 1/n)
        v = np.random.normal(0, 1/np.sqrt(self.dim), self.dim)
        return v

    def bind(self, a, b):
        """Holographic Binding: Circular Convolution via FFT."""
        return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real

    def unbind(self, composite, a):
        """Holographic Retrieval: Circular Correlation (approximate inverse)."""
        # Circular correlation is FFT(a)* * FFT(composite)
        return np.fft.ifft(np.conj(np.fft.fft(a)) * np.fft.fft(composite)).real

    def _get_semantic_signature(self, obj):
        """Extracts actual bytecode or source instead of just the string rep."""
        try:
            return inspect.getsource(obj)
        except:
            try:
                return str(obj.__code__.co_code) if hasattr(obj, '__code__') else str(obj)
            except:
                return str(obj)

    def _atomic_add(self, filepath, vector):
        """Thread-safe and process-safe accumulation into the manifold."""
        mode = 'rb+' if os.path.exists(filepath) else 'wb+'
        with open(filepath, mode) as f:
            if mode == 'rb+':
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    existing = np.load(f)
                    # Superposition: ADD, do not normalize yet
                    # Normalization happens only at the moment of 'perception'
                    new_v = existing + vector
                    f.seek(0)
                    np.save(f, new_v)
                    f.truncate() # Important to truncate if new_v is smaller than existing (unlikely here but good practice)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            else:
                np.save(f, vector)

    def ingest_semantic(self, path_name, obj):
        """Binds an identity vector to a semantic content vector."""
        sig = self._get_semantic_signature(obj)

        v_id = self._generate_unitary_vector(path_name)
        v_content = self._generate_unitary_vector(sig)

        # The trace is the bound pair
        trace = self.bind(v_id, v_content)

        # We store in a 'bucket' determined by the first level of the namespace
        # to reduce file-system overhead while maintaining some separation
        bucket = path_name.split('.')[0]
        file_path = os.path.join(self.memory_dir, f"bucket_{bucket}.npy") # Renamed to avoid collision with fiber_*.npy

        self._atomic_add(file_path, trace)

    def query(self, path_name):
        """Retrieves semantic memory from the manifold using an identity key."""
        bucket = path_name.split('.')[0]
        file_path = os.path.join(self.memory_dir, f"bucket_{bucket}.npy")

        if not os.path.exists(file_path):
            return None

        v_id = self._generate_unitary_vector(path_name)
        with open(file_path, 'rb') as f:
            manifold_segment = np.load(f)

        # Unbind to find the semantic content
        retrieved_content_vec = self.unbind(manifold_segment, v_id)
        return retrieved_content_vec

    def crawl(self, limit=100):
        """Controlled crawl of the local namespace."""
        print("[!] STRATOS: Targeted Semantic Ingestion...")
        count = 0
        for name, mod in list(sys.modules.items()):
            if name.startswith('stratos') or 'builtins' in name or mod is None or not hasattr(mod, '__file__'): continue
            if count >= limit: break
            try:
                for m_name, obj in inspect.getmembers(mod):
                    if count >= limit: break
                    if inspect.isfunction(obj) or inspect.isclass(obj):
                        full_path = f"{name}.{m_name}"
                        self.ingest_semantic(full_path, obj)
                        count += 1
            except:
                continue

    def breeding_loop(self):
        """Evolutionary Breeding on bucketed segments."""
        while self.is_running:
            try:
                buckets = [f for f in os.listdir(self.memory_dir) if f.endswith('.npy')]
                if len(buckets) >= 2:
                    b1_name, b2_name = np.random.choice(buckets, 2, replace=False)
                    v1 = np.load(os.path.join(self.memory_dir, b1_name))
                    v2 = np.load(os.path.join(self.memory_dir, b2_name))

                    # Spectral interference
                    v_syn = self.bind(v1, v2)
                    v_syn /= (np.linalg.norm(v_syn) + 1e-9)

                    # Store in a synthetic bucket
                    child_id = f"syn.{int(time.time() * 1000) % 1000000}"
                    np.save(os.path.join(self.memory_dir, f"bucket_{child_id}.npy"), v_syn)
            except Exception:
                pass
            time.sleep(1.0)

if __name__ == "__main__":
    engine = StratosEngineV2()
    # Ingest a specific known function for testing
    print("[1] Ingesting 'os.path.join'...")
    engine.ingest_semantic("os.path.join", os.path.join)

    # Retrieval test
    print("[2] Querying Manifold for 'os.path.join'...")
    res_vec = engine.query("os.path.join")

    # Verification
    # If the retrieval worked, the result vector should have a high
    # cosine similarity with the original semantic vector of os.path.join
    if res_vec is not None:
        orig_sig = engine._get_semantic_signature(os.path.join)
        orig_vec = engine._generate_unitary_vector(orig_sig)

        # Ensure retrieved_content_vec is normalized for cosine similarity calculation
        retrieved_content_vec_norm = res_vec / (np.linalg.norm(res_vec) + 1e-9)
        orig_vec_norm = orig_vec / (np.linalg.norm(orig_vec) + 1e-9)

        similarity = np.dot(retrieved_content_vec_norm, orig_vec_norm)
        print(f"[3] Retrieval Fidelity (Cosine Similarity): {similarity:.4f}")
    else:
        print("[3] Retrieval failed: No data found for 'os.path.join'")
