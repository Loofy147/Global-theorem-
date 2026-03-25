import itertools
from math import gcd
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
                    cur_idx = to_flat(cur);
                    if vis[cur_idx]: break
                    vis[cur_idx] = 1; cur = fg[cur]
        if comps != 1: return False
    return True

def solve_p1():
    m, k = 4, 4
    all_p = list(itertools.permutations(range(4)))

    # Try the "Nested Spike" hypothesis:
    # sigma(coords) = p[sum(coords)%m, coords[1]]
    # or something similar.

    # Let's try searching for a set of 4 permutations (one for each fiber level s)
    # assuming they are the same for all columns (fiber-uniform - but we know that fails)
    # So it must depend on j.

    # What if it's "diagonal"? p[s, j] = p_base[(s - j) % 4]
    for p_base in itertools.product(all_p, repeat=4):
        sigma = {}
        for coords in itertools.product(range(m), repeat=k):
            s = sum(coords) % m
            j = coords[1]
            sigma[coords] = p_base[(s - j) % m]
        if verify_k4(sigma, m):
            print(f"FOUND P1 DIAGONAL: {p_base}")
            return

    print("Diagonal search failed.")

if __name__ == "__main__":
    solve_p1()
