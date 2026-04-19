import hashlib
import hmac
import time
import base58
import itertools
import multiprocessing
from nacl.signing import SigningKey
from mnemonic import Mnemonic

def derive_solana_pubkey(seed_bytes, path="m/44'/501'/0'/0'"):
    try:
        I = hmac.new(b"ed25519 seed", seed_bytes, hashlib.sha512).digest()
        k, c = I[:32], I[32:]
        parts = path.split('/')
        if parts[0] == 'm': parts = parts[1:]
        for part in parts:
            idx = int(part[:-1]) | 0x80000000 if part.endswith("'") else int(part) | 0x80000000
            data = b"\x00" + k + idx.to_bytes(4, "big")
            I = hmac.new(c, data, hashlib.sha512).digest()
            k, c = I[:32], I[32:]
        return base58.b58encode(bytes(SigningKey(k).verify_key)).decode('utf-8')
    except:
        return None

def main():
    mnemo = Mnemonic("english")
    base = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
    lexicon = ["ability", "apple", "abandon", "zoo", "action", "allow", "brain", "bracket", "autumn", "actual"]
    target = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"

    print(f"[*] Starting Comprehensive Vault Recovery for: {target}")
    start_time = time.time()

    # 1. Check insertions of 'ability' and 'apple' (User's hinted words)
    print("[*] Phase 1: Checking insertions of 'ability' and 'apple'...")
    extra = ["ability", "apple"]
    found = False
    for i in range(11):
        for j in range(12):
            temp = list(base)
            temp.insert(i, extra[0])
            temp.insert(j, extra[1])
            phrase = " ".join(temp)
            if mnemo.check(phrase):
                seed = mnemo.to_seed(phrase)
                for path in ["m/44'/501'/0'/0'", "m/44'/501'/0'"]:
                    if derive_solana_pubkey(seed, path) == target:
                        print(f"\n[✓] SUCCESS: {phrase}")
                        print(f"[✓] Path: {path}")
                        return

    # 2. Check all 16,384 valid phrases starting with the 10 base words
    print("[*] Phase 2: Checking all valid phrases starting with base 10 words...")
    count = 0
    for w11 in mnemo.wordlist:
        prefix = base + [w11]
        for w12 in mnemo.wordlist:
            phrase = " ".join(prefix + [w12])
            if mnemo.check(phrase):
                count += 1
                seed = mnemo.to_seed(phrase)
                for path in ["m/44'/501'/0'/0'", "m/44'/501'/0'"]:
                    if derive_solana_pubkey(seed, path) == target:
                        print(f"\n[✓] SUCCESS: {phrase}")
                        print(f"[✓] Path: {path}")
                        return
        if time.time() - start_time > 120: break # Partial check

    # 3. Check permutations of 12 words (10 base + ability + apple) - Prefix-fixed
    print("[*] Phase 3: Checking permutations of 12 words (prefix-fixed)...")
    words_12 = base + extra
    for p_len in range(8, 3, -1):
        print(f" [*] Fixing first {p_len} words...")
        fixed = words_12[:p_len]
        variable = words_12[p_len:]
        for p in itertools.permutations(variable):
            phrase = " ".join(fixed + list(p))
            if mnemo.check(phrase):
                seed = mnemo.to_seed(phrase)
                for path in ["m/44'/501'/0'/0'", "m/44'/501'/0'"]:
                    if derive_solana_pubkey(seed, path) == target:
                        print(f"\n[✓] SUCCESS: {phrase}")
                        print(f"[✓] Path: {path}")
                        return
        if time.time() - start_time > 240: break

    # 4. Check combinations of Autopsy words
    print("[*] Phase 4: Checking Autopsy word combinations...")
    for w1, w2 in itertools.combinations(lexicon, 2):
        for i in range(11):
            for j in range(12):
                temp = list(base)
                temp.insert(i, w1)
                temp.insert(j, w2)
                phrase = " ".join(temp)
                if mnemo.check(phrase):
                    seed = mnemo.to_seed(phrase)
                    if derive_solana_pubkey(seed) == target:
                        print(f"\n[✓] SUCCESS: {phrase}")
                        return

    print("[-] Recovery failed in this environment. Suggest full local O(N^2) scan.")

if __name__ == "__main__":
    main()
