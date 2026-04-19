import hashlib
import hmac
import time
import base58
import itertools
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
    except: return None

def main():
    mnemo = Mnemonic("english")
    wl = mnemo.wordlist
    base = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]

    # Autopsy and Lexicon words
    sigmas = [20, 23, 53, 125, 214, 215, 497, 1574, 5, 86, 1, 2047]
    extra_candidates = [wl[s] for s in sigmas]

    target = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"
    print(f"[*] FSO VAULT BREAKER V2")
    print(f"[*] Target: {target}")

    start_time = time.time()
    found = False

    # 1. Insertion Search (All pairs of candidates, all positions, preserving base order)
    print("[*] Phase 1: Insertion Search with 12 extra candidates...")
    for w1, w2 in itertools.permutations(extra_candidates, 2):
        for i in range(11):
            for j in range(i + 1, 12):
                temp = list(base)
                temp.insert(i, w1)
                temp.insert(j, w2)
                phrase = " ".join(temp)
                if mnemo.check(phrase):
                    seed = mnemo.to_seed(phrase)
                    for path in ["m/44'/501'/0'/0'", "m/44'/501'/0'"]:
                        if derive_solana_pubkey(seed, path) == target:
                            print(f"\n[✓] SUCCESS! Phrase: {phrase} | Path: {path}")
                            return

    # 2. Check "Closure" for each candidate as 11th word
    print("[*] Phase 2: Closure Search (Each candidate as 11th word)...")
    for w11 in extra_candidates:
        prefix = base + [w11]
        for w12 in wl:
            phrase = " ".join(prefix + [w12])
            if mnemo.check(phrase):
                seed = mnemo.to_seed(phrase)
                if derive_solana_pubkey(seed) == target:
                    print(f"\n[✓] SUCCESS! Phrase: {phrase}")
                    return

    # 3. Check "Shifted" base words (Basin Escape)
    # Maybe "snack" is at index i, but it should be at index i + k?
    # Or maybe it's "snake"?
    print("[*] Phase 3: Basin Escape (Word substitution)...")
    # This might be too slow if we check all, so let's try just the first few words
    for idx in range(10):
        original = base[idx]
        # Check words within distance 2 in the wordlist
        orig_idx = wl.index(original)
        for offset in [-2, -1, 1, 2]:
            if 0 <= orig_idx + offset < 2048:
                new_word = wl[orig_idx + offset]
                temp_base = list(base)
                temp_base[idx] = new_word
                # Now find 11th and 12th from lexicon/autopsy
                for w11, w12 in itertools.permutations(extra_candidates, 2):
                    phrase = " ".join(temp_base + [w11, w12])
                    if mnemo.check(phrase):
                        seed = mnemo.to_seed(phrase)
                        if derive_solana_pubkey(seed) == target:
                            print(f"\n[✓] SUCCESS! Phrase: {phrase}")
                            return

    print("[-] Search exhausted.")

if __name__ == "__main__":
    main()
