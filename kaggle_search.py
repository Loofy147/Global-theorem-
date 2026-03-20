import sys, time, math, random
from math import gcd
from itertools import permutations, product as iprod
from typing import Optional, List, Dict, Tuple, Any

# --- CORE LOGIC (from core.py) ---

_ALL_P3 = [list(p) for p in permutations(range(3))]
_FIBER_SHIFTS = ((1,0),(0,1),(0,0))

def _build_sa3(m: int):
    n = m**3
    arc_s = [[0]*3 for _ in range(n)]
    for idx in range(n):
        i,rem = divmod(idx,m*m); j,k = divmod(rem,m)
        arc_s[idx][0] = ((i+1)%m)*m*m+j*m+k
        arc_s[idx][1] = i*m*m+((j+1)%m)*m+k
        arc_s[idx][2] = i*m*m+j*m+(k+1)%m
    pa = [[None]*3 for _ in range(6)]
    for pi,p in enumerate(_ALL_P3):
        for at,c in enumerate(p): pa[pi][c] = at
    return n, arc_s, pa

def _sa_score(sigma: List[int], arc_s, pa, n: int) -> int:
    f0=[0]*n; f1=[0]*n; f2=[0]*n
    for v in range(n):
        pi=sigma[v]; p=pa[pi]
        f0[v]=arc_s[v][p[0]]; f1[v]=arc_s[v][p[1]]; f2[v]=arc_s[v][p[2]]
    def cc(f):
        vis=bytearray(n); c=0
        for s in range(n):
            if not vis[s]:
                c+=1; cur=s
                while not vis[cur]: vis[cur]=1; cur=f[cur]
        return c
    return cc(f0)-1 + cc(f1)-1 + cc(f2)-1

def run_sa(m: int, seed: int=0, max_iter: int=10_000_000,
           T_init: float=3.0, T_min: float=0.003,
           verbose: bool=True, report_n: int=250_000):
    n, arc_s, pa = _build_sa3(m)
    rng = random.Random(seed); nP = 6
    sigma = [rng.randrange(nP) for _ in range(n)]
    cs = _sa_score(sigma, arc_s, pa, n)
    bs = cs; best = sigma[:]
    cool = (T_min/T_init)**(1.0/max_iter)
    T = T_init; stall=0; reheats=0; t0=time.perf_counter()

    for it in range(max_iter):
        if cs == 0: break
        if cs <= 2:
            vlist = list(range(n)); rng.shuffle(vlist)
            fixed = False
            for v in vlist:
                old = sigma[v]
                for pi in rng.sample(range(nP), nP):
                    if pi == old: continue
                    sigma[v] = pi
                    ns = _sa_score(sigma, arc_s, pa, n)
                    if ns < cs: cs=ns; fixed=True
                    if cs < bs: bs=cs; best=sigma[:]
                    if ns >= cs: sigma[v] = old
                    if fixed: break
                if fixed: break
            if cs == 0: break
            T *= cool; continue
        v=rng.randrange(n); old=sigma[v]; new=rng.randrange(nP)
        if new==old: T*=cool; continue
        sigma[v]=new; ns=_sa_score(sigma,arc_s,pa,n); d=ns-cs
        if d<0 or rng.random()<math.exp(-d/max(T,1e-9)):
            cs=ns
            if cs<bs: bs=cs; best=sigma[:]; stall=0
            else: stall+=1
        else: sigma[v]=old; stall+=1

        if stall > 100_000:
            reheats += 1; stall = 0
            sigma = best[:]; cs = bs
            T = T_init / (1.2**reheats)
            kick_size = max(1, n // 20)
            for _ in range(kick_size):
                vk = rng.randrange(n); sigma[vk] = rng.randrange(nP)
            cs = _sa_score(sigma, arc_s, pa, n)
            continue

        T*=cool
        if verbose and (it+1)%report_n==0:
            el=time.perf_counter()-t0
            print(f"it={it+1:>8,} T={T:.5f} s={cs} best={bs} reh={reheats} {el:.1f}s")

    elapsed=time.perf_counter()-t0
    sol=None
    if bs==0:
        sol={}
        for idx,pi in enumerate(best):
            i,rem=divmod(idx,m*m); j,k=divmod(rem,m)
            sol[(i,j,k)]=tuple(_ALL_P3[pi])
    return sol, {"best":bs,"iters":it+1,"elapsed":elapsed,"reheats":reheats}

# --- FRONTIER P2 SEARCH (m=6, k=3) ---

if __name__ == "__main__":
    print("=== Kaggle GPU Search: Problem P2 (m=6, k=3) ===")
    print("System: 216 vertices, full-3D SA engine v2.1")
    print(f"Iterations: 20,000,000  Basin-escape: ON")

    sol, stats = run_sa(6, seed=42, max_iter=20_000_000)

    print("\n--- Final Results ---")
    print(f"Status: {'SOLVED' if sol else 'OPEN'}")
    print(f"Best score: {stats['best']}")
    print(f"Total iterations: {stats['iters']:,}")
    print(f"Time elapsed: {stats['elapsed']:.1f}s")
    print(f"Total reheats: {stats['reheats']}")

    if sol:
        print("\nSolution sigma(v):")
        print(sol)
