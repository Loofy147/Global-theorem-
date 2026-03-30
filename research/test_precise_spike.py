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

def construct(m):
    # Base perms (arc_type -> color)
    ID = (0, 1, 2)  # 0->0, 1->1, 2->2
    S12 = (0, 2, 1) # 0->0, 1->2, 2->1
    S01 = (1, 0, 2) # 0->1, 1->0, 2->2

    # P[s] sequence
    base_seq = [ID] * (m-2) + [S12, S01]

    # Map color -> arc_type for table
    # table[s][j] = (arc_for_c0, arc_for_c1, arc_for_c2)
    table = []
    for s in range(m):
        p = base_seq[s]
        # p[arc] = color
        # we want pa[color] = arc
        pa = [0]*3
        for arc, color in enumerate(p):
            pa[color] = arc

        row = {}
        for j in range(m):
            cur_pa = list(pa)
            if j == m - 1:
                # Spike: swap02 (swap arc types 0 and 2)
                # This means color assigned to arc 0 now gets arc 2, and vice versa.
                # pa[c] = arc
                # color at arc 0 is c s.t. p[0] = c. pa[p[0]] = 0.
                # we want to swap values 0 and 2 in pa.
                # Actually, the proof says "swap02 swaps position 0 and 2".
                # If Pa is the tuple (arc_for_c0, arc_for_c1, arc_for_c2),
                # then swapping positions 0 and 2 in Pa means c0 and c2 swap their arcs.
                cur_pa[0], cur_pa[2] = cur_pa[2], cur_pa[0]
            row[j] = tuple(cur_pa)
        table.append(row)

    sigma = {}
    for i, j, k in iprod(range(m), range(m), range(m)):
        s = (i+j+k)%m
        sigma[(i,j,k)] = table[s][j]
    return sigma

for m in [3, 5, 7, 9]:
    sig = construct(m)
    res = verify_sigma_simple(sig, m)
    print(f"m={m}: {res}")
