import sys

def get_pa(s, m):
    # s < m-2 -> 1, s=m-2 -> 0, s=m-1 -> 2
    if s < m - 2: return [0, 1, 2]
    if s == m - 2: return [0, 2, 1]
    return [1, 0, 2]

def calculate_next_hop(current, color, m):
    x, y, z = current
    s = (x + y + z) % m
    pa = get_pa(s, m)

    # We need the correct Spike condition.
    # Original core.py says j == m - 1.
    # But in the sigma mapping sigma[(i,j,k)] = table[s][j],
    # i, j, k are the coordinates.
    # The coordinate j is the y-coordinate.
    if y == m - 1:
        pa[0], pa[2] = pa[2], pa[0]

    dim = pa[color]
    nxt = list(current)
    nxt[dim] = (nxt[dim] + 1) % m
    return tuple(nxt)

def verify(m):
    n = m**3
    all_edges = [set() for _ in range(3)]
    for c in range(3):
        vis = set()
        cur = (0, 0, 0)
        for _ in range(n):
            if cur in vis: return False, f"Color {c} repeat at {cur}"
            vis.add(cur)
            nxt = calculate_next_hop(cur, c, m)
            all_edges[c].add((cur, nxt))
            cur = nxt
        if len(vis) != n or cur != (0, 0, 0):
            return False, f"Color {c} not Hamiltonian (len={len(vis)}, final={cur})"

    for i in range(3):
        for j in range(i + 1, 3):
            if all_edges[i].intersection(all_edges[j]):
                return False, f"Colors {i} and {j} overlap"
    return True, "Success"

if __name__ == "__main__":
    for m in [3, 5, 7, 9]:
        ok, msg = verify(m)
        print(f"m={m}: {ok} {msg}")
