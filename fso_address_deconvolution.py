import numpy as np
import hashlib
import base58
from mnemonic import Mnemonic

def generate_vector(seed, dim=1024):
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    np.random.seed(h)
    v = np.random.randn(dim)
    return v / np.linalg.norm(v)

def unbind(bound_v, v_query):
    return np.fft.ifft(np.fft.fft(bound_v) * np.conj(np.fft.fft(v_query))).real

def main():
    addr = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"
    base_words = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    dim = 1024

    print(f"[*] FSO Deconvolution of Address: {addr}")

    # 1. Map Address to Vector
    addr_bytes = base58.b58decode(addr)
    # Pad to dim
    v_addr = np.zeros(dim)
    for i, b in enumerate(addr_bytes):
        v_addr[i % dim] += b
    v_addr = v_addr / np.linalg.norm(v_addr)

    # 2. Sum Knowns
    v_known = np.zeros(dim)
    for w in base_words:
        v_known += generate_vector(w, dim)
    v_known = v_known / np.linalg.norm(v_known)

    # 3. Unbind
    v_missing = unbind(v_addr, v_known)

    # 4. Resonance
    resonances = []
    for w in wordlist:
        v_w = generate_vector(w, dim)
        sim = np.dot(v_missing, v_w) / (np.linalg.norm(v_missing) * np.linalg.norm(v_w) + 1e-9)
        resonances.append((w, sim))

    resonances.sort(key=lambda x: x[1], reverse=True)
    print("\n[+] Top Resonances:")
    for w, s in resonances[:10]:
        print(f"    -> {w.upper()} ({s:.4f})")

    # Try different mapping for address
    print("\n[*] Trying different address mapping (MD5 of address)...")
    v_addr_2 = generate_vector(addr, dim)
    v_missing_2 = unbind(v_addr_2, v_known)

    resonances_2 = []
    for w in wordlist:
        v_w = generate_vector(w, dim)
        sim = np.dot(v_missing_2, v_w) / (np.linalg.norm(v_missing_2) * np.linalg.norm(v_w) + 1e-9)
        resonances_2.append((w, sim))

    resonances_2.sort(key=lambda x: x[1], reverse=True)
    for w, s in resonances_2[:10]:
        print(f"    -> {w.upper()} ({s:.4f})")

if __name__ == "__main__":
    main()
