import math, random, time, sys, os, json
from math import gcd
from itertools import permutations, product as iprod
from typing import Optional, List, Dict, Tuple, Any

# ══════════════════════════════════════════════════════════════════════════════
# UNIFIED ENGINE v2.2 (Basin Escape)
# ══════════════════════════════════════════════════════════════════════════════

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

def _sa_score(sigma: List[int], arc_s, pa, n: int, k: int=3) -> int:
    total_score = 0
    for c in range(k):
        vis = bytearray(n); comps = 0
        for s in range(n):
            if not vis[s]:
                comps += 1; cur = s
                while not vis[cur]:
                    vis[cur] = 1; pi = sigma[cur]
                    cur = arc_s[cur][pa[pi][c]]
        total_score += comps - 1
    return total_score

def run_fiber_structured_sa(m: int, k: int, seed: int=0, max_iter: int=10_000_000, verbose: bool=True):
    n, arc_s, pa, all_p = _build_sa(m, k); nP = len(all_p)
    def get_coords(idx):
        coords = []; val = idx
        for _ in range(k): coords.append(val % m); val //= m
        coords.reverse(); return coords
    fibers = [sum(get_coords(v)) % m for v in range(n)]
    def get_key(v):
        c = get_coords(v)
        return (fibers[v],) + tuple(c[1:-1])
    node_to_key = [get_key(v) for v in range(n)]
    keys = list(set(node_to_key))
    rng = random.Random(seed); tab = {k_: rng.randrange(nP) for k_ in keys}
    def make_sigma(t):
        sig = [0]*n
        for v in range(n): sig[v] = t[node_to_key[v]]
        return sig
    sigma = make_sigma(tab); cs = _sa_score(sigma, arc_s, pa, n, k); bs = cs; bt = tab.copy()
    T = 2.0; cool = 0.999999; t0 = time.perf_counter(); stall = 0
    for it in range(max_iter):
        if cs == 0: break
        if cs <= 20:
            # Basin Escape v2.2 for FiberSA
            rk_list = list(keys); rng.shuffle(rk_list); fixed = False
            for rk in rk_list:
                old = tab[rk]
                for pi in rng.sample(range(nP), nP):
                    if pi == old: continue
                    tab[rk] = pi; sig = make_sigma(tab)
                    ns = _sa_score(sig, arc_s, pa, n, k)
                    if ns < cs:
                        cs = ns; fixed = True
                        if cs < bs: bs = cs; bt = tab.copy()
                    else: tab[rk] = old
                    if fixed: break
                if fixed: break
            if not fixed:
                tab = bt.copy()
                for _ in range(max(1, int(len(keys)*0.05))): tab[rng.choice(keys)] = rng.randrange(nP)
                sig = make_sigma(tab); cs = _sa_score(sig, arc_s, pa, n, k)
            continue
        rk = rng.choice(keys); old = tab[rk]; tab[rk] = rng.randrange(nP)
        if tab[rk] == old: continue
        sig = make_sigma(tab); ns = _sa_score(sig, arc_s, pa, n, k); d = ns - cs
        if d <= 0 or rng.random() < math.exp(-d / T):
            cs = ns
            if cs < bs: bs = cs; bt = tab.copy(); stall = 0
            else: stall += 1
        else: tab[rk] = old; stall += 1
        if stall > 50_000:
            stall = 0; tab = bt.copy(); cs = bs
            for _ in range(max(1, int(len(keys)*0.05))): tab[rng.choice(keys)] = rng.randrange(nP)
            sig = make_sigma(tab); cs = _sa_score(sig, arc_s, pa, n, k); continue
        T *= cool
        if verbose and (it+1) % 100_000 == 0:
            print(f"  it={it+1:>8,} T={T:.5f} score={cs} best={bs} {time.perf_counter()-t0:.1f}s")
    sigma_final = make_sigma(bt)
    sol_dict = {}
    for i, pi in enumerate(sigma_final):
        coords = get_coords(i); sol_dict[str(tuple(coords))] = tuple(all_p[pi])
    return sigma_final if bs == 0 else None, {"best": bs, "iters": it+1, "solution": sol_dict if bs==0 else None}

if __name__ == "__main__":
    m, k, iters = 4, 4, 15_000_000
    print(f"Problem: P1 (m={m}, k={k}), Max Iters: {iters}")
    sol, stats = run_fiber_structured_sa(m=m, k=k, max_iter=iters)
    print(f"\nFinal Stats: {stats}")
    if sol:
        print("SOLUTION FOUND!")
        with open("solution.json", "w") as f:
            json.dump(stats.get("solution"), f)
