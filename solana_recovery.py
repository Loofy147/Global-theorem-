import hashlib
import hmac
import time
import base58
import nacl.bindings
from mnemonic import Mnemonic

def derive_solana_pubkey(seed_bytes, path="m/44'/501'/0'/0'"):
    # SLIP-0010 implementation for Ed25519
    i = hmac.new(b"ed25519 seed", seed_bytes, hashlib.sha512).digest()
    k_parent = i[:32]
    c_parent = i[32:]

    parts = path.split('/')
    if parts[0] == 'm': parts = parts[1:]

    for part in parts:
        index = int(part[:-1]) | 0x80000000 if part.endswith("'") else int(part) | 0x80000000
        data = b"\x00" + k_parent + index.to_bytes(4, "big")
        i = hmac.new(c_parent, data, hashlib.sha512).digest()
        k_parent = i[:32]
        c_parent = i[32:]

    public_key = nacl.bindings.crypto_sign_ed25519_sk_to_pk(k_parent)
    return base58.b58encode(public_key).decode('utf-8')

def recover():
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    base_words = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
    target_pubkey = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"

    print(f"[*] Starting recovery for: {target_pubkey}")
    start_time = time.time()

    # Pre-generate first 10 words string
    prefix = " ".join(base_words)

    found = False
    valid_count = 0

    # 2048 * 2048 = 4,194,304
    for i in range(2048):
        w11 = wordlist[i]
        for j in range(2048):
            w12 = wordlist[j]
            phrase = f"{prefix} {w11} {w12}"

            # FAST CHECKSUM FILTER (This is the "Parity Leak" in practice)
            if mnemo.check(phrase):
                valid_count += 1
                seed = mnemo.to_seed(phrase)
                # Check most common derivation path
                try:
                    pub = derive_solana_pubkey(seed)
                    if pub == target_pubkey:
                        print(f"\n[!!!] PHRASE FOUND: {phrase}")
                        print(f"[*] Latency: {time.time() - start_time:.2f}s")
                        found = True
                        break
                except:
                    pass
        if found: break
        if i % 100 == 0 and i > 0:
            elapsed = time.time() - start_time
            print(f"    ... Scanned {i}/2048 outer. Valid phrases checked: {valid_count}. Elapsed: {elapsed:.1f}s")

    if not found:
        print("\n[-] Phrase not found at the end of the sequence with path m/44'/501'/0'/0'.")

if __name__ == "__main__":
    recover()
