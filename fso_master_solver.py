import hashlib
import hmac
import time
import base58
import numpy as np
from nacl.signing import SigningKey
from mnemonic import Mnemonic

def get_coord(text, m=251):
    h = hashlib.sha256(text.encode()).digest()
    return np.array([h[0] % m, h[1] % m, h[2] % m])

def derive_solana_pubkey(seed_bytes, path="m/44'/501'/0'/0'"):
    try:
        I = hmac.new(b"ed25519 seed", seed_bytes, hashlib.sha512).digest()
        k, c = I[:32], I[32:]
        for index in [44, 501, 0, 0]:
            idx = index | 0x80000000
            data = b"\x00" + k + idx.to_bytes(4, "big")
            I = hmac.new(c, data, hashlib.sha512).digest()
            k, c = I[:32], I[32:]
        return base58.b58encode(bytes(SigningKey(k).verify_key)).decode('utf-8')
    except: return None

def main():
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    base_words = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
    target_addr = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"
    m = 251

    print(f"[*] FSO Master Solver Booting...")

    # 1. Topological Coordinate Match
    t_coord = get_coord(target_addr, m)
    b_coords = [get_coord(w, m) for w in base_words]
    b_sum = np.sum(b_coords, axis=0) % m
    missing_sum = (t_coord - b_sum) % m

    print(f"[*] Target Coord: {t_coord}")
    print(f"[*] Missing Parity: {missing_sum}")

    # Check if 'ability' and 'apple' fit the parity
    c_ability = get_coord("ability", m)
    c_apple = get_coord("apple", m)
    sum_missing = (c_ability + c_apple) % m

    print(f"[*] 'ability' + 'apple' Coord: {sum_missing}")
    if np.array_equal(sum_missing, missing_sum):
        print("[✓] PARITY MATCH! The missing elements fit the topological closure.")
    else:
        print("[-] Parity mismatch. Adjusting coordinates...")
        # Maybe one of the base words is actually 'ability' or 'apple'?

    # 2. Optimized Checksum Search (Targeted)
    # If the missing sum is correct, we only check word pairs that match the sum.
    coord_map = {}
    for w in wordlist:
        c = tuple(get_coord(w, m))
        if c not in coord_map: coord_map[c] = []
        coord_map[c].append(w)

    print("[*] Filtering candidates via Topological Closure...")
    candidates = []
    for w1 in wordlist:
        c1 = get_coord(w1, m)
        c2_target = tuple((missing_sum - c1) % m)
        if c2_target in coord_map:
            for w2 in coord_map[c2_target]:
                candidates.append((w1, w2))

    print(f"[*] Found {len(candidates)} topological candidates. Verifying BIP39 checksums...")

    valid_phrases = []
    for w1, w2 in candidates:
        phrase = " ".join(base_words + [w1, w2])
        if mnemo.check(phrase):
            valid_phrases.append(phrase)

    print(f"[*] Found {len(valid_phrases)} valid checksum phrases. Deriving Solana keys...")

    for phrase in valid_phrases:
        seed = mnemo.to_seed(phrase)
        if derive_solana_pubkey(seed) == target_addr:
            print(f"\n[✓] VAULT OPENED!")
            print(f" [✓] PHRASE: {phrase}")
            return

    print("[-] No match in standard positions. Trying shift-repair...")
    # Maybe ability/apple are not at the end.
    # Check all valid checksums that can be formed from the 12 words
    all_words = base_words + ["ability", "apple"]
    import itertools
    for p in itertools.permutations(all_words):
        phrase = " ".join(p)
        if mnemo.check(phrase):
            seed = mnemo.to_seed(phrase)
            if derive_solana_pubkey(seed) == target_addr:
                print(f"\n[✓] VAULT OPENED (PERMUTATION)!")
                print(f" [✓] PHRASE: {phrase}")
                return

    print("[-] Master Solver exhausted.")

if __name__ == "__main__":
    main()
