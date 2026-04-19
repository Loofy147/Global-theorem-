import hashlib
import hmac
import base58
from nacl.signing import SigningKey
from mnemonic import Mnemonic

def derive_solana_pubkey(seed_bytes):
    # Standard Solana derivation path m/44'/501'/0'/0'
    I = hmac.new(b"ed25519 seed", seed_bytes, hashlib.sha512).digest()
    k, c = I[:32], I[32:]
    for index in [44 | 0x80000000, 501 | 0x80000000, 0 | 0x80000000, 0 | 0x80000000]:
        data = b"\x00" + k + index.to_bytes(4, "big")
        I = hmac.new(c, data, hashlib.sha512).digest()
        k, c = I[:32], I[32:]
    return base58.b58encode(bytes(SigningKey(k).verify_key)).decode('utf-8')

def main():
    mnemo = Mnemonic("english")
    wl = mnemo.wordlist
    base = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
    target = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"

    # Sigmas from the TGI Autopsy
    sigmas = [20, 23, 53, 125, 214, 215] # action, actual, allow, autumn, bracket, brain
    # Missing elements mentioned by user
    lexicon = ["ability", "apple"]

    candidates = [wl[s] for s in sigmas] + lexicon

    print(f"[*] FSO Sigma Solver")
    print(f"[*] Target: {target}")
    print(f"[*] Candidates: {candidates}")

    import itertools
    found = False

    # 1. Try all pairs of candidates as word 11 and 12
    for w11, w12 in itertools.permutations(candidates, 2):
        phrase = " ".join(base + [w11, w12])
        if mnemo.check(phrase):
            seed = mnemo.to_seed(phrase)
            if derive_solana_pubkey(seed) == target:
                print(f"\n[✓] VAULT OPENED!")
                print(f" [✓] PHRASE: {phrase}")
                found = True
                break

    if not found:
        # 2. Try replacing one word from the base and adding one
        print("[*] Phase 2: Single substitution + 1 addition...")
        for i in range(10):
            for sub in candidates:
                temp_base = list(base)
                temp_base[i] = sub
                remaining = [c for c in candidates if c != sub]
                for extra in remaining:
                    # Try extra at 11th, closure at 12th
                    prefix = temp_base + [extra]
                    for word in wl:
                        phrase = " ".join(prefix + [word])
                        if mnemo.check(phrase):
                            seed = mnemo.to_seed(phrase)
                            if derive_solana_pubkey(seed) == target:
                                print(f"\n[✓] VAULT OPENED VIA REPAIR!")
                                print(f" [✓] PHRASE: {phrase}")
                                return

    if not found:
        print("[-] Search complete.")

if __name__ == "__main__":
    main()
