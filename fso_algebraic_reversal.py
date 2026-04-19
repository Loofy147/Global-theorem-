import numpy as np
import hashlib
from mnemonic import Mnemonic

def generate_vector(seed, dim=1024):
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    np.random.seed(h)
    v = np.random.randn(dim)
    return v / np.linalg.norm(v)

mnemo = Mnemonic("english")
wordlist = mnemo.wordlist
base_words = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
target_address = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"

print(f"[*] FSO Algebraic Reversal for: {target_address}")

# 1. Map target and knowns to the manifold
dim = 1024
v_target = generate_vector(target_address, dim)
v_known = np.zeros(dim)
for w in base_words:
    v_known += generate_vector(w, dim)

# 2. Algebraic Deconvolution (Subtraction)
v_missing = v_target - v_known

# 3. Resonance Resolution
resonances = []
for w in wordlist:
    v_w = generate_vector(w, dim)
    sim = np.dot(v_missing, v_w) / (np.linalg.norm(v_missing) * np.linalg.norm(v_w) + 1e-9)
    resonances.append((w, sim))

resonances.sort(key=lambda x: x[1], reverse=True)

print("\n[+] Top Geometric Resonances:")
for w, score in resonances[:10]:
    print(f"    -> {w.upper()} (Energy: {score:.4f})")

# 4. Verification of top candidates
top_words = [w for w, s in resonances[:20]]
print("\n[*] Verifying combinations of top candidates...")

import hmac
from nacl.signing import SigningKey
import base58

def derive_solana_pubkey(seed_bytes):
    I = hmac.new(b"ed25519 seed", seed_bytes, hashlib.sha512).digest()
    k, c = I[:32], I[32:]
    for index in [44 | 0x80000000, 501 | 0x80000000, 0 | 0x80000000, 0 | 0x80000000]:
        data = b"\x00" + k + index.to_bytes(4, "big")
        I = hmac.new(c, data, hashlib.sha512).digest()
        k, c = I[:32], I[32:]
    return base58.b58encode(bytes(SigningKey(k).verify_key)).decode('utf-8')

found = False
import itertools
for w1, w2 in itertools.permutations(top_words, 2):
    phrase = " ".join(base_words + [w1, w2])
    if mnemo.check(phrase):
        seed = mnemo.to_seed(phrase)
        if derive_solana_pubkey(seed) == target_address:
            print(f"\n[✓] VAULT OPENED!")
            print(f" [✓] PHRASE: {phrase}")
            found = True
            break

    # Try insertion?
    for i in range(11):
        for j in range(i+1, 12):
            temp = list(base_words)
            temp.insert(i, w1)
            temp.insert(j, w2)
            phrase = " ".join(temp)
            if mnemo.check(phrase):
                seed = mnemo.to_seed(phrase)
                if derive_solana_pubkey(seed) == target_address:
                    print(f"\n[✓] VAULT OPENED (INSERTION)!")
                    print(f" [✓] PHRASE: {phrase}")
                    found = True
                    break
        if found: break
    if found: break

if not found:
    print("\n[-] Reversal failed. Trying top candidates as single replacements...")
    for idx in range(10):
        for rep in top_words:
            temp = list(base_words)
            temp[idx] = rep
            # Try adding one more word from top_words
            for extra in top_words:
                for pos in range(11):
                    p_list = list(temp)
                    p_list.insert(pos, extra)
                    phrase = " ".join(p_list)
                    if mnemo.check(phrase):
                        seed = mnemo.to_seed(phrase)
                        if derive_solana_pubkey(seed) == target_address:
                            print(f"\n[✓] VAULT OPENED (REPAIR)!")
                            print(f" [✓] PHRASE: {phrase}")
                            found = True
                            break
                if found: break
            if found: break
        if found: break

if not found:
    print("[-] No phrase found using top resonance candidates.")
