import hashlib
import hmac
import time
import base58
import multiprocessing
from nacl.signing import SigningKey
from mnemonic import Mnemonic

def derive_solana_pubkey(seed, path_indices):
    I = hmac.new(b"ed25519 seed", seed, hashlib.sha512).digest()
    k, c = I[:32], I[32:]
    for index in path_indices:
        idx = index | 0x80000000
        data = b"\x00" + k + idx.to_bytes(4, "big")
        I = hmac.new(c, data, hashlib.sha512).digest()
        k, c = I[:32], I[32:]
    return base58.b58encode(bytes(SigningKey(k).verify_key)).decode('utf-8')

def worker(chunk_start, chunk_end, prefix_words, target, wordlist, path_indices, pipe):
    mnemo = Mnemonic("english")
    prefix = " ".join(prefix_words)
    for i in range(chunk_start, chunk_end):
        w1 = wordlist[i]
        for w2 in wordlist:
            phrase = f"{prefix} {w1} {w2}"
            if mnemo.check(phrase):
                seed = mnemo.to_seed(phrase)
                if derive_solana_pubkey(seed, path_indices) == target:
                    pipe.send(phrase)
                    return
    pipe.send(None)

def main():
    target = "7jDVmS8HBdDNdtGXSxepjcktvG6FzbPurZvYUVgY7TG5"
    base_words = ["snack", "right", "wedding", "gun", "canal", "pet", "rescue", "hand", "scheme", "head"]
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist

    # Path m/44'/501'/0'
    path = [44, 501, 0]

    print(f"[*] Checking path m/44'/501'/0' for: {target}")
    start_time = time.time()

    num_procs = 4
    chunk_size = 2048 // num_procs
    parent_conns = []
    procs = []
    for i in range(num_procs):
        parent_conn, child_conn = multiprocessing.Pipe()
        parent_conns.append(parent_conn)
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_procs - 1 else 2048
        p = multiprocessing.Process(target=worker, args=(start, end, base_words, target, wordlist, path, child_conn))
        p.start()
        procs.append(p)

    finished = 0
    while finished < num_procs:
        for conn in parent_conns:
            if conn.poll():
                res = conn.recv()
                if res is None: finished += 1
                else:
                    print(f"\n[✓] PHRASE FOUND: {res}")
                    for p in procs: p.terminate()
                    return
        if time.time() - start_time > 150: # Limit to 2.5 min
            print("[!] Timeout for path m/44'/501'/0'")
            for p in procs: p.terminate()
            break

    # Check "Missing words at beginning"
    print(f"[*] Checking missing words at BEGINNING (path m/44'/501'/0'/0')...")
    def worker_begin(chunk_start, chunk_end, suffix_words, target, wordlist, pipe):
        mnemo = Mnemonic("english")
        suffix = " ".join(suffix_words)
        for i in range(chunk_start, chunk_end):
            w1 = wordlist[i]
            for w2 in wordlist:
                phrase = f"{w1} {w2} {suffix}"
                if mnemo.check(phrase):
                    seed = mnemo.to_seed(phrase)
                    if derive_solana_pubkey(seed, [44, 501, 0, 0]) == target:
                        pipe.send(phrase)
                        return
        pipe.send(None)

    procs = []
    parent_conns = []
    for i in range(num_procs):
        parent_conn, child_conn = multiprocessing.Pipe()
        parent_conns.append(parent_conn)
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_procs - 1 else 2048
        p = multiprocessing.Process(target=worker_begin, args=(start, end, base_words, target, wordlist, child_conn))
        p.start()
        procs.append(p)

    finished = 0
    while finished < num_procs:
        for conn in parent_conns:
            if conn.poll():
                res = conn.recv()
                if res is None: finished += 1
                else:
                    print(f"\n[✓] PHRASE FOUND (at beginning): {res}")
                    for p in procs: p.terminate()
                    return
        if time.time() - start_time > 300:
            print("[!] Total Timeout.")
            for p in procs: p.terminate()
            break

if __name__ == "__main__":
    main()
