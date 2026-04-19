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
wl = mnemo.wordlist
base = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
target = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"

# The user's words
missing = ["ability", "apple"]

print(f"Target: {target}")

def check_prefix(prefix):
    # For a given 11 words, there are multiple valid 12th words (usually 8-16)
    # Actually for 12 words, it's 128 bits + 4 bits checksum.
    # 11 words = 121 bits. 12th word = 7 bits of entropy + 4 bits of checksum.
    # So 2^7 = 128 words.
    for w12 in wl:
        phrase = " ".join(prefix + [w12])
        if mnemo.check(phrase):
            seed = mnemo.to_seed(phrase)
            if derive_solana_pubkey(seed) == target:
                return phrase
    return None

# Try prefixes
print("[*] Checking prefix: base + ability")
res = check_prefix(base + ["ability"])
if res: print(f"FOUND: {res}"); exit(0)

print("[*] Checking prefix: base + apple")
res = check_prefix(base + ["apple"])
if res: print(f"FOUND: {res}"); exit(0)

# Try permutations where one of ability/apple is NOT at the end
all_12 = base + missing
import itertools
print("[*] Checking permutations of the 12 words (subset)...")
# Since 12! is too big, let's just check if ability and apple are in the phrase.
# I already checked prefix-fixed permutations.

# What if "apple" is the 12th word?
print("[*] Checking phrases where 'apple' is the 12th word...")
for w11 in wl:
    phrase = " ".join(base + [w11, "apple"])
    if mnemo.check(phrase):
        seed = mnemo.to_seed(phrase)
        if derive_solana_pubkey(seed) == target:
            print(f"FOUND: {phrase}"); exit(0)

# What if "ability" is the 12th word?
print("[*] Checking phrases where 'ability' is the 12th word...")
for w11 in wl:
    phrase = " ".join(base + [w11, "ability"])
    if mnemo.check(phrase):
        seed = mnemo.to_seed(phrase)
        if derive_solana_pubkey(seed) == target:
            print(f"FOUND: {phrase}"); exit(0)

print("[-] No match found.")
