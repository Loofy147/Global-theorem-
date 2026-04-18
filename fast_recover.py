import hashlib
import hmac
import time
import base58
import nacl.bindings
from mnemonic import Mnemonic

def derive_solana_pubkey(seed_bytes):
    i = hmac.new(b"ed25519 seed", seed_bytes, hashlib.sha512).digest()
    k = i[:32]
    c = i[32:]
    # path m/44'/501'/0'/0'
    for index in [44 | 0x80000000, 501 | 0x80000000, 0 | 0x80000000, 0 | 0x80000000]:
        data = b"\x00" + k + index.to_bytes(4, "big")
        i = hmac.new(c, data, hashlib.sha512).digest()
        k, c = i[:32], i[32:]
    public_key = nacl.bindings.crypto_sign_ed25519_sk_to_pk(k)
    return base58.b58encode(public_key).decode('utf-8')

mnemo = Mnemonic("english")
wordlist = mnemo.wordlist
prefix_words = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
target = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"

print(f"Target: {target}")
start = time.time()
count = 0
found = False

# Try words that start with 'a' first as a hint from the user's example
sorted_wordlist = sorted(wordlist)

for w11 in wordlist:
    for w12 in wordlist:
        phrase = " ".join(prefix_words + [w11, w12])
        if mnemo.check(phrase):
            count += 1
            seed = mnemo.to_seed(phrase)
            if derive_solana_pubkey(seed) == target:
                print(f"FOUND: {phrase}")
                found = True
                break
    if found: break
    if count % 1000 == 0 and count > 0:
        print(f"Checked {count} valid phrases... Time: {time.time()-start:.1f}s")
    # Stop if we've been running for too long (limit to 300s)
    if time.time() - start > 300:
        print("Timeout reached.")
        break

if not found:
    print("Search ended.")
