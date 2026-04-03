import sys
from itertools import product as iprod

def verify_sigma(sigma, m):
    n = m**3
    all_edges = [set() for _ in range(3)]
    for c in range(3):
        vis = set()
        cur = (0, 0, 0)
        for _ in range(n):
            if cur in vis: return False, f"Color {c} repeat at {cur}"
            vis.add(cur)
            p = sigma.get(cur)
            if not p: return False, f"No sigma for {cur}"
            arc = p[c]
            nxt = list(cur); nxt[arc] = (nxt[arc] + 1) % m
            nxt = tuple(nxt)
            all_edges[c].add((cur, nxt))
            cur = nxt
        if len(vis) != n or cur != (0, 0, 0):
            return False, f"Color {c} not Hamiltonian (len={len(vis)}, final={cur})"

    for i in range(3):
        for j in range(i + 1, 3):
            if all_edges[i].intersection(all_edges[j]):
                return False, f"Colors {i} and {j} overlap"
    return True, "Success"

def construct_spike_sigma_fixed(m):
    # Deterministic sequence for j_movers
    if m == 3:
        j_movers = [1, 0, 2]
    else:
        j_movers = [1] * (m - 2) + [0, 2]

    table = []
    for s in range(m):
        jm = j_movers[s]
        others = sorted([c for c in range(3) if c != jm])
        o1, o2 = others[0], others[1]
        row = {}
        for j in range(m):
            p = [0, 0, 0]
            p[1] = jm
            # The swap logic: p[0] and p[2] are o1, o2
            if j == m - 1:
                p[0], p[2] = o1, o2
            else:
                p[0], p[2] = o2, o1
            row[j] = tuple(p)
        table.append(row)

    sigma = {}
    for i, j, k in iprod(range(m), range(m), range(m)):
        s = (i+j+k)%m
        sigma[(i,j,k)] = table[s][j]
    return sigma

if __name__ == "__main__":
    for m in [3, 5, 7, 9]:
        sig = construct_spike_sigma_fixed(m)
        ok, msg = verify_sigma(sig, m)
        print(f"m={m}: {ok} {msg}")
