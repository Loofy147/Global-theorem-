import hashlib
import hmac
import base58
from nacl.signing import SigningKey
from mnemonic import Mnemonic

def derive_solana_pubkey(seed_bytes):
    I = hmac.new(b"ed25519 seed", seed_bytes, hashlib.sha512).digest()
    k, c = I[:32], I[32:]
    for index in [44 | 0x80000000, 501 | 0x80000000, 0 | 0x80000000, 0 | 0x80000000]:
        data = b"\x00" + k + index.to_bytes(4, "big")
        I = hmac.new(c, data, hashlib.sha512).digest()
        k, c = I[:32], I[32:]
    return base58.b58encode(bytes(SigningKey(k).verify_key)).decode('utf-8')

mnemo = Mnemonic("english")
base = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
# Sigma indices from autopsy: 20 (action), 23 (actual), 53 (allow), 125 (autumn), 214 (bracket), 215 (brain)
# Plus the user's "missing elements": ability (1), apple (99)
sigma_words = ["action", "actual", "allow", "autumn", "bracket", "brain", "ability", "apple"]
target = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"

print(f"[*] Checking Sigma/Lexicon word combinations for: {target}")

found = False
# Case 1: One Sigma word + One Closure word at the end
for sigma in sigma_words:
    for word12 in mnemo.wordlist:
        phrase = " ".join(base + [sigma, word12])
        if mnemo.check(phrase):
            if derive_solana_pubkey(mnemo.to_seed(phrase)) == target:
                print(f"\n[✓] MATCH FOUND: {phrase}")
                found = True
                break
    if found: break

if not found:
    # Case 2: One Closure word + One Sigma word at the end
    for word11 in mnemo.wordlist:
        for sigma in sigma_words:
            phrase = " ".join(base + [word11, sigma])
            if mnemo.check(phrase):
                if derive_solana_pubkey(mnemo.to_seed(phrase)) == target:
                    print(f"\n[✓] MATCH FOUND: {phrase}")
                    found = True
                    break
        if found: break

if not found:
    # Case 3: Two Sigma words anywhere in the 12 words
    import itertools
    for s1, s2 in itertools.permutations(sigma_words, 2):
        for i in range(11):
            for j in range(12):
                temp = list(base)
                temp.insert(i, s1)
                temp.insert(j, s2)
                phrase = " ".join(temp)
                if mnemo.check(phrase):
                    if derive_solana_pubkey(mnemo.to_seed(phrase)) == target:
                        print(f"\n[✓] MATCH FOUND: {phrase}")
                        found = True
                        break
            if found: break
        if found: break

if not found:
    print("[-] Sigma search failed.")
