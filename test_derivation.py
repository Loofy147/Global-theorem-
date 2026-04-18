import hashlib
import hmac
import base58
import nacl.bindings
from mnemonic import Mnemonic

def derive_solana_pubkey(seed_bytes, path="m/44'/501'/0'/0'"):
    HARDENED = 0x80000000
    # Parse path
    parts = path.split('/')
    if parts[0] == 'm':
        parts = parts[1:]

    # Master key derivation (SLIP-0010)
    I = hmac.new(b"ed25519 seed", seed_bytes, hashlib.sha512).digest()
    key = I[:32]
    chain_code = I[32:]

    for part in parts:
        if part.endswith("'"):
            index = int(part[:-1]) + HARDENED
        else:
            index = int(part)

        data = b'\x00' + key + index.to_bytes(4, byteorder='big')
        I = hmac.new(chain_code, data, hashlib.sha512).digest()
        key = I[:32]
        chain_code = I[32:]

    public_key = nacl.bindings.crypto_sign_ed25519_sk_to_pk(key)
    return base58.b58encode(public_key).decode('utf-8')

# Test with a known phrase
# Phrase: abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
# Expected Solana Address (standard): Gig7... or something else?
# Let's check with mnemonic
mnemo = Mnemonic("english")
test_phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
seed = mnemo.to_seed(test_phrase)
try:
    addr = derive_solana_pubkey(seed)
    print(f"Phrase: {test_phrase}")
    print(f"Address: {addr}")
except Exception as e:
    print(f"Error: {e}")

# Try another path m/44'/501'/0'
try:
    addr2 = derive_solana_pubkey(seed, path="m/44'/501'/0'")
    print(f"Address (m/44'/501'/0'): {addr2}")
except Exception as e:
    print(f"Error 2: {e}")
