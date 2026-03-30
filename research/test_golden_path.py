import sys, os
from math import gcd
from itertools import product as iprod

def verify_sigma_simple(sigma, m):
    for c in range(3):
        vis = set(); cur = (0,0,0)
        for _ in range(m**3):
            if cur in vis: return False
            vis.add(cur); p = sigma.get(cur)
            arc = p[c]; nxt = list(cur); nxt[arc] = (nxt[arc] + 1) % m
            cur = tuple(nxt)
        if len(vis) != m**3 or cur != (0,0,0): return False
    return True

def construct_golden(m):
    # P[s] sequence:
    # Color 1 gets arc 1 at m-2 levels -> IDENTITY (0,1,2)
    # Color 2 gets arc 1 at 1 level    -> SWAP12 (0,2,1)
    # Color 0 gets arc 1 at 1 level    -> SWAP01 (1,0,2)

    # We need an assignment arc_type -> color
    # P_s maps arc_type to color.
    # Level s=0..m-3: arc 1 -> color 1. ID = (0, 1, 2)
    # Level s=m-2:   arc 1 -> color 2. S12 = (0, 2, 1)
    # Level s=m-1:   arc 1 -> color 0. S01 = (1, 0, 2)

    table = []
    for s in range(m):
        if s < m - 2:   p = (0, 1, 2)
        elif s == m - 2: p = (0, 2, 1)
        else:           p = (1, 0, 2)

        # Color c's arc is pa[c] where p[pa[c]] = c
        pa = [0]*3
        for arc, color in enumerate(p):
            pa[color] = arc

        row = {}
        for j in range(m):
            cur_pa = list(pa)
            if j == m - 1:
                # Spike: swap02
                # Positions 0 and 2 in the permutation p swap.
                # p' = p \circ (0, 2)
                # p'[0] = p[2], p'[2] = p[0], p'[1] = p[1].
                # This means color at arc 0 and color at arc 2 swap their arc assignments.
                # In pa (color -> arc), this means pa[p[0]] and pa[p[2]] swap values.
                # Since pa[p[0]] = 0 and pa[p[2]] = 2, we just swap positions 0 and 2? No.
                # "swaps position 0 and 2" usually means in the sequence.
                # If row[j] = (arc_c0, arc_c1, arc_c2), then swap02 means
                # (arc_c2, arc_c1, arc_c0)? No, that's swapping colors c0 and c2.
                # "swaps position 0 and 2" of the arc types.
                # arc 0 becomes arc 2, arc 2 becomes arc 0.
                # pa[c] = arc.
                # If pa[c] was 0, it becomes 2. If it was 2, it becomes 0.
                for c in range(3):
                    if cur_pa[c] == 0: cur_pa[c] = 2
                    elif cur_pa[c] == 2: cur_pa[c] = 0
            row[j] = tuple(cur_pa)
        table.append(row)

    sigma = {}
    for i, j, k in iprod(range(m), range(m), range(m)):
        s = (i+j+k)%m
        sigma[(i,j,k)] = table[s][j]
    return sigma

for m in [3, 5, 7, 9]:
    sig = construct_golden(m)
    res = verify_sigma_simple(sig, m)
    print(f"m={m}: {res}")
