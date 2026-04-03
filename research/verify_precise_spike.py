import sys, os
from itertools import product as iprod

def get_arc(i, j, k, color, m):
    s = (i+j+k) % m
    if s < m - 2:
        pa = [0, 1, 2]
    elif s == m - 2:
        pa = [0, 2, 1]
    else: # s == m - 1
        pa = [1, 0, 2]

    if j == m - 1:
        pa[0], pa[2] = pa[2], pa[0]

    return pa[color]

def verify_precise_spike(m):
    print(f"--- Verifying Precise Spike for m={m} ---")
    all_edges = [set() for _ in range(3)]

    for color in range(3):
        vis = set()
        cur = (0, 0, 0)
        for step in range(m**3):
            if cur in vis:
                print(f"  Color {color} FAILED: Repeated node {cur} at step {step}")
                return False
            vis.add(cur)

            arc = get_arc(cur[0], cur[1], cur[2], color, m)
            nxt = list(cur)
            nxt[arc] = (nxt[arc] + 1) % m
            nxt_tuple = tuple(nxt)

            all_edges[color].add((cur, nxt_tuple))
            cur = nxt_tuple

        if len(vis) != m**3:
            print(f"  Color {color} FAILED: Visited only {len(vis)} nodes")
            return False
        if cur != (0, 0, 0):
            print(f"  Color {color} FAILED: Did not return to origin")
            return False
        print(f"  Color {color} PASSED (Hamiltonian)")

    # Check edge disjointness
    for i in range(3):
        for j in range(i + 1, 3):
            isect = all_edges[i].intersection(all_edges[j])
            if isect:
                print(f"  Colors {i} and {j} overlap at {len(isect)} edges!")
                return False
            else:
                print(f"  Colors {i} and {j} are edge-disjoint")
    return True

if __name__ == "__main__":
    for m in [3, 5, 7, 9]:
        if not verify_precise_spike(m):
            sys.exit(1)
