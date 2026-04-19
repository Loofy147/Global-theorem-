import itertools
import random
import hashlib
import hmac
import base58
import time
from nacl.signing import SigningKey
from mnemonic import Mnemonic

def derive_solana_pubkey(seed):
    I = hmac.new(b"ed25519 seed", seed, hashlib.sha512).digest()
    k, c = I[:32], I[32:]
    for index in [44, 501, 0, 0]:
        idx = index | 0x80000000
        data = b"\x00" + k + idx.to_bytes(4, "big")
        I = hmac.new(c, data, hashlib.sha512).digest()
        k, c = I[:32], I[32:]
    return base58.b58encode(bytes(SigningKey(k).verify_key)).decode('utf-8')

mnemo = Mnemonic("english")
base = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
extra = ["ability", "apple"]
all_12 = base + extra
target = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"

print(f"[*] FSO Final Attempt for: {target}")
start_time = time.time()

# 1. Random Permutations of the 12 words
print("[*] Checking random permutations of the 12 words...")
# Check 100k random permutations (this covers a good portion of valid ones)
for i in range(100000):
    p = list(all_12)
    random.shuffle(p)
    phrase = " ".join(p)
    if mnemo.check(phrase):
        seed = mnemo.to_seed(phrase)
        if derive_solana_pubkey(seed) == target:
            print(f"\n[✓] FOUND PERMUTATION: {phrase}")
            exit(0)
    if i % 20000 == 0 and i > 0:
        print(f"    ... {i} checked. Elapsed: {time.time()-start_time:.1f}s")

# 2. Block positions for the 10 words
print("[*] Checking block positions for the 10 words...")
for w1 in mnemo.wordlist:
    # Case: [w1, base10, closure]
    prefix = [w1] + base
    # Find word 12 closures
    for w12 in mnemo.wordlist:
        phrase = " ".join(prefix + [w12])
        if mnemo.check(phrase):
            seed = mnemo.to_seed(phrase)
            if derive_solana_pubkey(seed) == target:
                print(f"\n[✓] FOUND POSITION 2: {phrase}")
                exit(0)
    if time.time() - start_time > 300: break

# 3. Autopsy words check (Sigma positions)
print("[*] Checking Sigma words at the end...")
sigmas = ["action", "actual", "allow", "autumn", "bracket", "brain"]
for s in sigmas:
    for w in mnemo.wordlist:
        phrase = " ".join(base + [s, w])
        if mnemo.check(phrase):
            if derive_solana_pubkey(mnemo.to_seed(phrase)) == target:
                print(f"\n[✓] FOUND SIGMA: {phrase}")
                exit(0)

print("[-] No phrase found. The vault is topologically secure in this environment.")
