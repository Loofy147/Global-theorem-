import math, random, time, sys, os
from math import gcd
from itertools import permutations, product as iprod

def _build_sa(m: int, k: int=3):
    n = m**k
    arc_s = [[0]*k for _ in range(n)]
    m_pow = [m**i for i in range(k)]
    m_pow.reverse()
    for idx in range(n):
        for c in range(k):
            if (idx // m_pow[c]) % m == m - 1:
                arc_s[idx][c] = idx - (m - 1) * m_pow[c]
            else:
                arc_s[idx][c] = idx + m_pow[c]
    all_p = [list(p) for p in permutations(range(k))]
    pa = [[None]*k for _ in range(len(all_p))]
    for pi,p in enumerate(all_p):
        for at,c in enumerate(p): pa[pi][c] = at
    return n, arc_s, pa, all_p

def _sa_score(sigma, arc_s, pa, n, k):
    total = 0
    for c in range(k):
        vis = bytearray(n); comps = 0
        for s in range(n):
            if not vis[s]:
                comps += 1; cur = s
                while not vis[cur]:
                    vis[cur] = 1; pi = sigma[cur]
                    cur = arc_s[cur][pa[pi][c]]
        total += comps - 1
    return total

def search_m6_k4(max_iter=1_000_000, seed=42):
    m, k = 6, 4
    n, arc_s, pa, all_p = _build_sa(m, k); nP = len(all_p)
    rng = random.Random(seed); sigma = [rng.randrange(nP) for _ in range(n)]
    cs = _sa_score(sigma, arc_s, pa, n, k); bs = cs
    T = 2.0; cool = 0.999998; t0 = time.perf_counter()
    for it in range(max_iter):
        if cs == 0: break
        v = rng.randrange(n); old = sigma[v]; sigma[v] = rng.randrange(nP)
        ns = _sa_score(sigma, arc_s, pa, n, k); d = ns - cs
        if d <= 0 or rng.random() < math.exp(-d/T):
            cs = ns
            if cs < bs: bs = cs; print(f"  it={it+1} score={cs} best={bs} {time.perf_counter()-t0:.1f}s")
        else: sigma[v] = old
        T *= cool
    return bs

if __name__ == "__main__":
    search_m6_k4()
