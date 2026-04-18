import hashlib
import hmac
import base58
import nacl.bindings
from mnemonic import Mnemonic

def derive_solana_pubkey(seed_bytes, path="m/44'/501'/0'/0'"):
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

mnemo = Mnemonic("english")
phrase = "snack right wedding gun canal pet rescue hand scheme head ability apple"
print(f"Checking phrase: {phrase}")
if mnemo.check(phrase):
    seed = mnemo.to_seed(phrase)
    pub = derive_solana_pubkey(seed)
    print(f"Derived Address: {pub}")
    print(f"Target Address:  7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5")
    if pub == "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5":
        print("MATCH FOUND!")
    else:
        print("NO MATCH.")
else:
    print("INVALID CHECKSUM.")
