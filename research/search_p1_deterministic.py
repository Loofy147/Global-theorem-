import itertools
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import verify_sigma

def verify_k4(sigma, m):
    k = 4; n = m**k
    sh = [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]
    funcs = [{} for _ in range(k)]
    for v, p in sigma.items():
        for at in range(k):
            nb = tuple((v[d] + sh[at][d]) % m for d in range(k))
            funcs[p[at]][v] = nb
    for fg in funcs:
        vis = bytearray(n); comps = 0
        def to_flat(coords):
            res = 0
            for x in coords: res = res * m + x
            return res
        for s_coords in fg:
            s_idx = to_flat(s_coords)
            if not vis[s_idx]:
                comps += 1; cur = s_coords
                while True:
                    cur_idx = to_flat(cur)
                    if vis[cur_idx]: break
                    vis[cur_idx] = 1; cur = fg[cur]
        if comps != 1: return False
    return True

def search():
    m, k = 4, 4
    all_p = list(itertools.permutations(range(4)))

    # Hypothesis: sigma depends on (s, j%2)
    # 8 perms total.
    import random
    rng = random.Random(42)

    print("Searching for P1 (m=4, k=4) with (s, j%2) symmetry...")
    for it in range(1000000):
        # 4 perms for j%2==0, 4 for j%2==1
        ps = [rng.choice(all_p) for _ in range(8)]
        sigma = {}
        for coords in itertools.product(range(m), repeat=k):
            s = sum(coords) % m
            j_mod = coords[1] % 2
            sigma[coords] = ps[s + j_mod*4]

        if verify_k4(sigma, m):
            print(f"FOUND P1: {ps}")
            return
    print("Not found in 1M iterations.")

if __name__ == "__main__":
    search()
