import math, random, time, json, os, sys
from typing import List, Tuple, Dict, Any, Optional
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

def get_node_orbits(m: int, k: int, generators: List[Tuple[int, ...]]) -> List[List[int]]:
    n = m**k; unvisited = set(range(n)); orbits = []
    while unvisited:
        start = next(iter(unvisited)); orbit = {start}
        queue = [start]; unvisited.remove(start)
        while queue:
            curr = queue.pop(0)
            coords = []
            tmp = curr
            for _ in range(k): coords.append(tmp % m); tmp //= m
            coords.reverse()
            for gen in generators:
                nxt_c = [(coords[d] + gen[d]) % m for d in range(k)]
                nxt = 0
                for x in nxt_c: nxt = nxt * m + x
                if nxt in unvisited:
                    unvisited.remove(nxt); orbit.add(nxt); queue.append(nxt)
        orbits.append(list(orbit))
    return orbits

def run_frontier_sa(m: int, k: int=3, seed: int=42, max_iter: int=1_000_000, verbose=True):
    if verbose: print(f"\n--- Frontier Search: m={m}, k={k} (seed={seed}) ---")
    n, arc_s, pa, all_p = _build_sa(m, k); nP = len(all_p)

    # Orbit generators for symmetry-aware search
    # For even m, we use m/2 and 2-step shifts
    gens = []
    if m % 2 == 0: gens.append(tuple([m//2]*k))
    if m % 3 == 0: gens.append(tuple([m//3]*k))
    if not gens: gens.append(tuple([1]*k))

    orbits = get_node_orbits(m, k, gens)
    if verbose: print(f"  Orbit count: {len(orbits)}")

    rng = random.Random(seed); sigma = [rng.randrange(nP) for _ in range(n)]
    cs = _sa_score(sigma, arc_s, pa, n, k); bs = cs; best = sigma[:]

    T = 2.0; cool = 0.999995; t0 = time.perf_counter(); stall = 0; reh = 0

    for it in range(max_iter):
        if cs == 0: break

        # Basin Escape v3.3 logic
        if cs <= 15:
            # Basin break moves are greedy
            shuffled_orbits = orbits[:]
            rng.shuffle(shuffled_orbits)
            fixed = False
            for orbit in shuffled_orbits[:50]:
                old_vals = [sigma[v] for v in orbit]
                for pi in rng.sample(range(nP), nP):
                    if all(sigma[v] == pi for v in orbit): continue
                    for v in orbit: sigma[v] = pi
                    ns = _sa_score(sigma, arc_s, pa, n, k)
                    if ns < cs:
                        cs = ns; fixed = True
                        if cs < bs: bs = cs; best = sigma[:]
                        break
                    else:
                        for i, v in enumerate(orbit): sigma[v] = old_vals[i]
                if fixed: break

            if not fixed:
                # Orbit-swap
                for _ in range(200):
                    o1, o2 = rng.sample(orbits, 2)
                    old1 = [sigma[v] for v in o1]; old2 = [sigma[v] for v in o2]
                    p1, p2 = rng.randrange(nP), rng.randrange(nP)
                    for v in o1: sigma[v] = p1
                    for v in o2: sigma[v] = p2
                    ns = _sa_score(sigma, arc_s, pa, n, k)
                    if ns < cs:
                        cs = ns; fixed = True
                        if cs < bs: bs = cs; best = sigma[:]
                        break
                    else:
                        for i, v in enumerate(o1): sigma[v] = old1[i]
                        for i, v in enumerate(o2): sigma[v] = old2[i]

            if not fixed:
                # Reheat / Kick
                reh += 1; sigma = best[:]; cs = bs; T = 1.0; stall = 0
                for _ in range(max(1, int(n * (0.05 if cs > 20 else 0.02)))):
                    sigma[rng.randrange(n)] = rng.randrange(nP)
                cs = _sa_score(sigma, arc_s, pa, n, k)
            continue

        # Equivariant SA
        if rng.random() < 0.4:
            orbit = rng.choice(orbits); new_p = rng.randrange(nP)
            old_vals = [sigma[v] for v in orbit]
            for v in orbit: sigma[v] = new_p
            ns = _sa_score(sigma, arc_s, pa, n, k); d = ns - cs
            if d <= 0 or rng.random() < math.exp(-d/T):
                cs = ns
                if cs < bs: bs = cs; best = sigma[:]; stall = 0
                else: stall += 1
            else:
                for i, v in enumerate(orbit): sigma[v] = old_vals[i]
                stall += 1
        else:
            v = rng.randrange(n); old = sigma[v]; sigma[v] = rng.randrange(nP)
            ns = _sa_score(sigma, arc_s, pa, n, k); d = ns - cs
            if d <= 0 or rng.random() < math.exp(-d/T):
                cs = ns
                if cs < bs: bs = cs; best = sigma[:]; stall = 0
                else: stall += 1
            else:
                sigma[v] = old; stall += 1

        if stall > 150_000:
            reh += 1; stall = 0; sigma = best[:]; cs = bs; T = 2.0 / (1.1 ** reh)
            for _ in range(max(1, int(n * 0.05))):
                sigma[rng.randrange(n)] = rng.randrange(nP)
            cs = _sa_score(sigma, arc_s, pa, n, k)

        T *= cool
        if verbose and (it+1) % 100_000 == 0:
            print(f"    it={it+1:>8,} score={cs} best={bs} T={T:.5f} reh={reh} {time.perf_counter()-t0:.1f}s")

    if verbose: print(f"  Final Best: {bs} (elapsed={time.perf_counter()-t0:.1f}s)")
    return best if bs == 0 else None, {"best": bs, "reheats": reh}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python frontier_discovery.py <m> <k> [iters] [seed]")
        sys.exit(1)
    m = int(sys.argv[1]); k = int(sys.argv[2])
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 1_000_000
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 42
    run_frontier_sa(m, k, seed, iters)
