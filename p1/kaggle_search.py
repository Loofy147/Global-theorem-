import math, random, time, sys, os, json
from math import gcd
from itertools import permutations, product as iprod
from typing import Optional, List, Dict, Tuple, Any

# ══════════════════════════════════════════════════════════════════════════════
# UNIFIED ENGINE v3.0 (Basin Escape)
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

def get_node_orbits(m: int, k: int, subgroup_generators: List[Tuple[int, ...]]) -> List[List[int]]:
    n = m**k; unvisited = set(range(n)); orbits = []
    while unvisited:
        start_idx = next(iter(unvisited)); orbit = {start_idx}
        queue = [start_idx]; unvisited.remove(start_idx)
        while queue:
            curr_idx = queue.pop(0)
            curr_coords = []; val = curr_idx
            for _ in range(k): curr_coords.append(val % m); val //= m
            curr_coords.reverse()
            for gen in subgroup_generators:
                nxt_coords = [(curr_coords[d] + gen[d]) % m for d in range(k)]
                nxt_idx = 0
                for x in nxt_coords: nxt_idx = nxt_idx * m + x
                if nxt_idx in unvisited:
                    unvisited.remove(nxt_idx); orbit.add(nxt_idx); queue.append(nxt_idx)
        orbits.append(list(orbit))
    return orbits

def run_hybrid_sa(m: int, k: int=3, seed: int=0, max_iter: int=10_000_000, verbose: bool=True):
    n, arc_s, pa, all_p = _build_sa(m, k); nP = len(all_p)
    gens = [tuple([m//2]*k)] if m%2==0 else [tuple([1]*k)]
    orbits = get_node_orbits(m, k, gens)
    rng = random.Random(seed); sigma = [rng.randrange(nP) for _ in range(n)]
    cs = _sa_score(sigma, arc_s, pa, n, k); bs = cs; best = sigma[:]
    T = 2.0; cool = (0.003/2.0)**(1.0/max_iter) if max_iter > 0 else 0.999998
    t0 = time.perf_counter(); stall = 0; reheats = 0
    for it in range(max_iter):
        if cs == 0: break
        if cs <= 15:
            # Basin Escape v3.0
            order = list(range(n)); rng.shuffle(order); fixed = False
            for v in order:
                old = sigma[v]
                for pi in rng.sample(range(nP), nP):
                    if pi == old: continue
                    sigma[v] = pi; ns = _sa_score(sigma, arc_s, pa, n, k)
                    if ns < cs:
                        cs = ns; fixed = True
                        if cs < bs: bs = cs; best = sigma[:]
                    else: sigma[v] = old
                    if fixed: break
                if fixed: break
            if not fixed:
                for orbit in rng.sample(orbits, min(len(orbits), 20)):
                    old_vals = [sigma[v] for v in orbit]
                    for pi in rng.sample(range(nP), nP):
                        if all(sigma[v] == pi for v in orbit): continue
                        for v in orbit: sigma[v] = pi
                        ns = _sa_score(sigma, arc_s, pa, n, k)
                        if ns < cs:
                            cs = ns; fixed = True
                            if cs < bs: bs = cs; best = sigma[:]
                        else:
                            for i, v in enumerate(orbit): sigma[v] = old_vals[i]
                        if fixed: break
                    if fixed: break
            if not fixed:
                v_list = list(range(n)); rng.shuffle(v_list)
                for i in range(min(n, 40)):
                    v1 = v_list[i]
                    for j in range(i+1, min(n, 80)):
                        v2 = v_list[j]; old1, old2 = sigma[v1], sigma[v2]
                        for _ in range(10):
                            pi1, pi2 = rng.randrange(nP), rng.randrange(nP)
                            sigma[v1], sigma[v2] = pi1, pi2
                            ns = _sa_score(sigma, arc_s, pa, n, k)
                            if ns < cs:
                                cs = ns; fixed = True
                                if cs < bs: bs = cs; best = sigma[:]
                                break
                            else: sigma[v1], sigma[v2] = old1, old2
                        if fixed: break
                    if fixed: break
            if not fixed:
                reheats += 1; stall = 0; sigma = best[:]; cs = bs; T = 1.0
                for _ in range(max(1, int(n * 0.05))):
                    vk = rng.randrange(n); sigma[vk] = rng.randrange(nP)
                cs = _sa_score(sigma, arc_s, pa, n, k)
            continue
        rk = rng.randrange(n); old = sigma[rk]; sigma[rk] = rng.randrange(nP)
        ns = _sa_score(sigma, arc_s, pa, n, k); d = ns - cs
        if d <= 0 or rng.random() < math.exp(-d / T):
            cs = ns
            if cs < bs: bs = cs; best = sigma[:]; stall = 0
            else: stall += 1
        else: sigma[rk] = old; stall += 1
        if stall > 100_000:
            reheats += 1; stall = 0; sigma = best[:]; cs = bs; T = 2.0 / (1.2**reheats)
            for _ in range(max(1, int(n * 0.05))):
                vk = rng.randrange(n); sigma[vk] = rng.randrange(nP)
            cs = _sa_score(sigma, arc_s, pa, n, k); continue
        T *= cool
        if verbose and (it+1) % 100_000 == 0:
            print(f"  it={it+1:>8,} T={T:.5f} score={cs} best={bs} reh={reheats} {time.perf_counter()-t0:.1f}s")
    return best if bs == 0 else None, {"best": bs, "iters": it+1}

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
    T = 2.0; cool = (0.003/2.0)**(1.0/max_iter) if max_iter > 0 else 0.999998
    t0 = time.perf_counter(); stall = 0
    for it in range(max_iter):
        if cs == 0: break
        if cs <= 15:
            # Basin Escape v3.0 for FiberSA
            fixed = False
            rk_list = list(keys); rng.shuffle(rk_list)
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
                pairs = []
                for idx1 in range(len(rk_list)):
                    for idx2 in range(idx1 + 1, len(rk_list)):
                        pairs.append((rk_list[idx1], rk_list[idx2]))
                rng.shuffle(pairs)
                for k1, k2 in pairs[:50]:
                    old1, old2 = tab[k1], tab[k2]
                    for _ in range(20):
                        pi1, pi2 = rng.randrange(nP), rng.randrange(nP)
                        tab[k1], tab[k2] = pi1, pi2
                        sig = make_sigma(tab)
                        ns = _sa_score(sig, arc_s, pa, n, k)
                        if ns < cs:
                            cs = ns; fixed = True
                            if cs < bs: bs = cs; bt = tab.copy()
                            break
                        else: tab[k1], tab[k2] = old1, old2
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
    problem = os.environ.get("KAGGLE_PROBLEM", "P3")
    m = int(os.environ.get("KAGGLE_M", 8))
    k = int(os.environ.get("KAGGLE_K", 3))
    engine = os.environ.get("KAGGLE_ENGINE", "hybrid")
    iters = int(os.environ.get("MAX_ITER", 30_000_000))
    seed = random.randint(0, 1000000)
    print(f"Problem: {problem} (m={m}, k={k}), Max Iters: {iters}, Seed: {seed}, Engine: {engine}")
    if engine == "fiber":
        sol, stats = run_fiber_structured_sa(m=m, k=k, seed=seed, max_iter=iters)
    else:
        sol, stats = run_hybrid_sa(m=m, k=k, seed=seed, max_iter=iters)
    print(f"\nFinal Stats: {stats}")
    if sol:
        print("SOLUTION FOUND!")
        with open("solution.json", "w") as f:
            json.dump(stats.get("solution", sol), f)
