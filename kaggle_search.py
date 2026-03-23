import math, random, time, sys, os, json
from math import gcd, log2
from itertools import permutations, product as iprod
from typing import Optional, List, Dict, Tuple, Any

# ══════════════════════════════════════════════════════════════════════════════
# PROBLEM 1: k=4, m=4 (G_4^4)
# ══════════════════════════════════════════════════════════════════════════════

def run_p1_sa(max_iter=5_000_000, seed=42):
    M=4; K=4; N=M**4
    ALL_P4 = list(permutations(range(K))); nP=len(ALL_P4)
    def dec4(v):
        l=v%4; v//=4; k_=v%4; v//=4; j_=v%4; i_=v//4
        return i_,j_,k_,l
    def enc4(i,j,k_,l): return i*64+j*16+k_*4+l
    arc_s=[[0]*K for _ in range(N)]
    for v in range(N):
        ci,cj,ck,cl=dec4(v); arc_s[v][0]=enc4((ci+1)%M,cj,ck,cl); arc_s[v][1]=enc4(ci,(cj+1)%M,ck,cl)
        arc_s[v][2]=enc4(ci,cj,(ck+1)%M,cl); arc_s[v][3]=enc4(ci,cj,ck,(cl+1)%M)
    pa=[[None]*K for _ in range(nP)]
    for pi,p in enumerate(ALL_P4):
        for at,c in enumerate(p): pa[pi][c]=at

    rng=random.Random(seed); sigma=[rng.randrange(nP) for _ in range(N)]
    def get_score(sig):
        f=[[0]*N for _ in range(K)]
        for v in range(N):
            pi=sig[v]; p=pa[pi]
            for c in range(K): f[c][v]=arc_s[v][p[c]]
        def cc(fg):
            vis=bytearray(N); comps=0
            for s in range(N):
                if not vis[s]:
                    comps+=1; cur=s
                    while not vis[cur]: vis[cur]=1; cur=fg[cur]
            return comps
        return sum(cc(f[c])-1 for c in range(K))

    cs=get_score(sigma); bs=cs; best=sigma[:]; T=5.0; cool=0.999998
    t0=time.perf_counter()
    for it in range(max_iter):
        if cs==0: break
        v=rng.randrange(N); old=sigma[v]; sigma[v]=rng.randrange(nP)
        ns=get_score(sigma); d=ns-cs
        if d<=0 or rng.random() < math.exp(-d/T):
            cs=ns
            if cs<bs: bs=cs; best=sigma[:]
        else: sigma[v]=old
        T*=cool
        if (it+1)%100_000==0:
            print(f"  it={it+1} score={cs} best={bs} T={T:.4f} {time.perf_counter()-t0:.1f}s")
    return best if bs==0 else None, {"best": bs, "iters": it+1}

# ══════════════════════════════════════════════════════════════════════════════
# PROBLEM 2: m=6, k=3 (G_6^3)
# ══════════════════════════════════════════════════════════════════════════════

def run_p2_equivariant_sa(max_iter=10_000_000, seed=42):
    m=6; k=3; n=m**3
    ALL_P3 = [list(p) for p in permutations(range(3))]; nP=6
    arc_s = [[0]*3 for _ in range(n)]
    for idx in range(n):
        i,rem = divmod(idx,m*m); j,k_ = divmod(rem,m)
        arc_s[idx][0] = ((i+1)%m)*m*m+j*m+k_; arc_s[idx][1] = i*m*m+((j+1)%m)*m+k_; arc_s[idx][2] = i*m*m+j*m+(k_+1)%m
    pa = [[None]*3 for _ in range(6)]
    for pi,p in enumerate(ALL_P3):
        for at,c in enumerate(p): pa[pi][c] = at

    def get_score(sig):
        f = [[0]*n for _ in range(3)]
        for v in range(n):
            pi=sig[v]; p=pa[pi]
            for c in range(3): f[c][v]=arc_s[v][p[c]]
        def cc(fg):
            vis=bytearray(n); c=0
            for s in range(n):
                if not vis[s]:
                    c+=1; cur=s
                    while not vis[cur]: vis[cur]=1; cur=fg[cur]
            return c
        return sum(cc(f[c])-1 for c in range(3))

    nodes = [(i,j,k_) for i in range(m) for j in range(m) for k_ in range(m)]
    node_to_idx = {v: i for i, v in enumerate(nodes)}
    unvisited = set(range(n)); orbits = []
    gens = [(3,3,3)] # Z2 orbit
    while unvisited:
        start_idx = next(iter(unvisited)); start_node = nodes[start_idx]; orbit = {start_idx}
        queue = [start_node]; unvisited.remove(start_idx)
        while queue:
            curr = queue.pop(0)
            for gen in gens:
                nxt = tuple((curr[d] + gen[d]) % m for d in range(3))
                nxt_idx = node_to_idx[nxt]
                if nxt_idx in unvisited: unvisited.remove(nxt_idx); orbit.add(nxt_idx); queue.append(nxt)
        orbits.append(list(orbit))

    rng=random.Random(seed); sigma=[rng.randrange(nP) for _ in range(n)]
    cs=get_score(sigma); bs=cs; best=sigma[:]; T=2.0; cool=0.999998; t0=time.perf_counter()
    for it in range(max_iter):
        if cs==0: break
        orbit=rng.choice(orbits); new_p=rng.randrange(nP); old_vals=[sigma[v] for v in orbit]
        for v in orbit: sigma[v]=new_p
        ns=get_score(sigma); d=ns-cs
        if d<=0 or rng.random() < math.exp(-d/T):
            cs=ns
            if cs<bs: bs=cs; best=sigma[:]
        else:
            for i,v in enumerate(orbit): sigma[v]=old_vals[i]
        T*=cool
        if (it+1)%100_000==0:
            print(f"  it={it+1} score={cs} best={bs} T={T:.4f} {time.perf_counter()-t0:.1f}s")
    return best if bs==0 else None, {"best": bs, "iters": it+1}

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    problem = os.environ.get("KAGGLE_PROBLEM", "P2")
    iters = int(os.environ.get("MAX_ITER", 10_000_000))
    seed = int(os.environ.get("SEED", 42))

    if problem == "P1":
        sol, stats = run_p1_sa(max_iter=iters, seed=seed)
    else:
        sol, stats = run_p2_equivariant_sa(max_iter=iters, seed=seed)

    print(f"\nFinal Stats: {stats}")
    if sol:
        print("SOLUTION FOUND!")
        with open("solution.json", "w") as f:
            json.dump(sol, f)

if __name__ == "__main__":
    main()
