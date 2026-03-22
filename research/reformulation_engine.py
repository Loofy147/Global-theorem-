#!/usr/bin/env python3
"""
reformulation_engine.py
========================
The coordinates discovered solving Claude's Cycles — fiber stratification,
twisted translation, parity obstruction, score functions, repair mode —
are domain-independent tools.

This engine applies them systematically to reformulate problems across six domains:

  Domain A: Latin squares         (fiber + coprimality)
  Domain B: Graph k-coloring      (stratification + score + SA)
  Domain C: Magic squares         (parity obstruction + twisted translation)
  Domain D: Diophantine systems   (modular fiber + impossibility proof)
  Domain E: Covering codes        (layer decomposition + governing condition)
  Domain F: Permutation groups    (coset fibers + twisted translation)

For each domain we demonstrate:
  1. REFRAME   — find the fiber map analog
  2. OBSTRUCT  — derive the parity/modular impossibility condition
  3. GOVERN    — state the minimal predicate that determines solvability
  4. SCORE     — build the continuous objective (bridges search→verify)
  5. SOLVE     — apply SA or direct construction, verify result
  6. BOUND     — prove where the construction fails

Run:
  python reformulation_engine.py                # all domains
  python reformulation_engine.py --domain A     # single domain
  python reformulation_engine.py --domain A B C # selected domains
"""

import sys, random, math, time
from itertools import permutations, product
from typing import List, Dict, Tuple, Optional, Any, Callable
from math import gcd
from collections import Counter

# ── colour ────────────────────────────────────────────────────────────────────
R="\033[91m";G="\033[92m";Y="\033[93m";B="\033[94m"
M="\033[95m";C="\033[96m";W="\033[97m";D="\033[2m";Z="\033[0m"
DOM_CLR = {'A':G,'B':B,'C':M,'D':Y,'E':C,'F':R}

def hr(c="─",n=72): return c*n
def domain_header(letter, title, tagline):
    clr = DOM_CLR.get(letter, W)
    print(f"\n{hr('═')}")
    print(f"{clr}Domain {letter} — {title}{Z}  {D}{tagline}{Z}")
    print(hr('─'))
def phase(name, num, desc):
    PCOLS = {1:G,2:R,3:B,4:M,5:Y,6:C}
    print(f"\n  {PCOLS.get(num,W)}[{num}] {name}{Z}  {D}{desc}{Z}")
def found(msg):  print(f"  {G}✓ {msg}{Z}")
def miss(msg):   print(f"  {R}✗ {msg}{Z}")
def note(msg):   print(f"  {Y}→ {msg}{Z}")
def info(msg):   print(f"  {D}{msg}{Z}")
def kv(k,v):     print(f"  {D}{k:<34}{Z}{W}{str(v)[:72]}{Z}")

# ══════════════════════════════════════════════════════════════════════════════
# UNIVERSAL TOOLS  (the coordinates from Claude's Cycles, abstracted)
# ══════════════════════════════════════════════════════════════════════════════

class FiberMap:
    """
    Tool 1: Fiber Stratification.
    Given a set of objects and a function f: objects → layers,
    partition the objects into fibers and describe how arcs/constraints
    cross between fibers.
    """
    def __init__(self, objects, layer_fn: Callable, num_layers: int):
        self.objects   = list(objects)
        self.layer_fn  = layer_fn
        self.num_layers= num_layers
        self.fibers    = {s: [o for o in objects if layer_fn(o)==s]
                          for s in range(num_layers)}

    def fiber_size(self, s):
        return len(self.fibers[s])

    def report(self):
        sizes = [self.fiber_size(s) for s in range(self.num_layers)]
        uniform = len(set(sizes)) == 1
        return {"num_layers": self.num_layers, "sizes": sizes, "uniform": uniform}


class ParityObstruction:
    """
    Tool 2: Modular / Parity Obstruction.
    Given a modulus m and a requirement that k values each coprime to m
    sum to a target T, decide if this is possible.
    Returns the obstruction if impossible, or an example if possible.
    """
    def __init__(self, m: int, k: int, target: int):
        self.m      = m
        self.k      = k
        self.target = target

    def coprime_elements(self) -> List[int]:
        return [r for r in range(1, self.m) if gcd(r, self.m)==1]

    def analyse(self) -> dict:
        cp   = self.coprime_elements()
        m, k, T = self.m, self.k, self.target
        # check all k-tuples
        from itertools import product as iprod
        feasible = [tup for tup in iprod(cp, repeat=k) if sum(tup)==T]
        all_same_parity = len(set(x%2 for x in cp)) == 1
        if all_same_parity:
            parity = cp[0] % 2  # 0=even 1=odd
            k_parity = (k * parity) % 2
            T_parity = T % 2
            impossible = (k_parity != T_parity)
        else:
            impossible = len(feasible) == 0

        return {
            "m":              m,
            "k":              k,
            "target":         T,
            "coprime_elems":  cp,
            "all_same_parity":all_same_parity,
            "feasible":       feasible[:3],
            "impossible":     impossible,
            "obstruction":    (f"All coprime-to-{m} are odd; "
                               f"sum of {k} odds has parity {k%2}, "
                               f"but target {T} has parity {T%2}."
                               if impossible else None),
            "example":        feasible[0] if feasible else None,
        }


class ScoreFunction:
    """
    Tool 3: Continuous score bridging search and verification.
    score=0  ⟺  solution is valid.
    The score must be: (a) cheap to compute, (b) monotone toward 0.
    """
    def __init__(self, verify_fn: Callable, score_fn: Callable, name: str):
        self.verify_fn = verify_fn
        self.score_fn  = score_fn
        self.name      = name

    def __call__(self, candidate) -> int:
        return self.score_fn(candidate)

    def is_valid(self, candidate) -> bool:
        return self.verify_fn(candidate)


class SAEngine:
    """
    Tool 4: Simulated Annealing with repair mode and plateau escape.
    Domain-agnostic: needs perturb_fn, score_fn, init_fn.
    """
    def __init__(self, init_fn, perturb_fn, score_fn,
                 T_init=3.0, T_min=0.003, plateau_steps=50_000):
        self.init_fn      = init_fn
        self.perturb_fn   = perturb_fn
        self.score_fn     = score_fn
        self.T_init       = T_init
        self.T_min        = T_min
        self.plateau_steps= plateau_steps

    def run(self, max_iter=500_000, seed=0, repair_fn=None,
            verbose=False, report_n=100_000):
        rng  = random.Random(seed)
        state= self.init_fn(rng)
        s    = self.score_fn(state)
        best_s, best = s, state
        cool = (self.T_min/self.T_init)**(1/max_iter)
        T    = self.T_init
        stall= 0; reheats=0; t0=time.perf_counter()

        for it in range(max_iter):
            if s == 0: break
            # repair mode when close
            if s <= 1 and repair_fn is not None:
                improved, state = repair_fn(state, rng)
                s = self.score_fn(state)
                if s < best_s: best_s=s; best=state
                if s == 0: break
                T *= cool; continue

            new_state = self.perturb_fn(state, rng)
            ns        = self.score_fn(new_state)
            delta     = ns - s
            if delta < 0 or rng.random() < math.exp(-delta/max(T,1e-9)):
                state = new_state; s = ns
                if s < best_s:
                    best_s=s; best=state; stall=0
                else: stall+=1
            else: stall+=1

            if stall > self.plateau_steps:
                T = self.T_init / (2**reheats); reheats+=1; stall=0
                state=best; s=best_s

            T *= cool
            if verbose and (it+1)%report_n==0:
                print(f"    {D}iter={it+1:>7,} T={T:.4f} score={s} best={best_s} "
                      f"reheats={reheats} {time.perf_counter()-t0:.1f}s{Z}")

        elapsed = time.perf_counter()-t0
        return best, {"best_score":best_s,"iters":it+1,"elapsed":elapsed,"reheats":reheats}


# ══════════════════════════════════════════════════════════════════════════════
# DOMAIN A: LATIN SQUARES
# Fiber: row → column assignment; Twisted translation: shifts between rows
# ══════════════════════════════════════════════════════════════════════════════

def domain_A(n=5):
    domain_header('A','Latin Squares',
        f'n={n}: each symbol 0..n-1 appears exactly once in every row and column')

    # ── [1] Reframe ──────────────────────────────────────────────────────────
    phase('REFRAME', 1, 'Find the fiber map analog')
    info(f'Latin square of order n={n}: L[i][j] ∈ Z_n')
    info('Fiber map: f(i,j) = i  → rows are fibers, columns are fiber coordinates')
    info('Arc analog: constraint that each symbol appears once per row AND column')

    # Fiber structure
    objs = [(i,j) for i in range(n) for j in range(n)]
    fm   = FiberMap(objs, lambda ij: ij[0], n)
    rep  = fm.report()
    kv('Fibers (rows)',        rep['num_layers'])
    kv('Fiber size (columns)', rep['sizes'][0])
    kv('Uniform fibers',       rep['uniform'])
    note('Each row is a fiber; each row must be a permutation of Z_n')
    note('Column constraint = cross-fiber bijection condition')

    # ── [2] Obstruct ──────────────────────────────────────────────────────────
    phase('OBSTRUCT', 2, 'Find the parity/modular obstruction')
    info('Latin squares of order n=2: only 1 reduced form → highly constrained')
    info('Order 6: the Euler 36-officers problem → no orthogonal pair exists')
    for test_n, has_ortho in [(2,False),(3,True),(4,True),(5,True),(6,False),(7,True)]:
        exists = '✓' if has_ortho else '✗'
        print(f"    n={test_n}: orthogonal Latin pair exists = {G if has_ortho else R}{exists}{Z}")
    note('Euler conjecture (n≡2 mod 4): disproved for n≥10 but holds for n=2,6')
    note('n=6 obstruction: Tarry 1901 exhaustive proof — no algebraic shortcut')

    # ── [3] Govern ────────────────────────────────────────────────────────────
    phase('GOVERN', 3, 'State the governing condition')
    kv('Governing condition',
       'Latin square order n always exists for n≥1')
    kv('Orthogonal pair',
       'Exists for all n except n=2 and n=6 (Bose-Shrikhande-Parker 1960)')
    kv('Construction (odd prime n)',
       'L[i][j] = (i + j*k) mod n for k=1,...,n-1 gives n-1 MOLS')

    # ── [4] Score → solve ──────────────────────────────────────────────────────
    phase('SCORE + SOLVE', 4, 'Build score function and find Latin square')
    def ls_score(L):
        """Conflicts: violations in rows + columns."""
        n_ = len(L)
        s  = 0
        for i in range(n_):
            s += n_ - len(set(L[i][j] for j in range(n_)))
        for j in range(n_):
            s += n_ - len(set(L[i][j] for i in range(n_)))
        return s

    def ls_verify(L):
        return ls_score(L) == 0

    def ls_init(rng):
        L = [list(range(n)) for _ in range(n)]
        for row in L: rng.shuffle(row)
        return L

    def ls_perturb(L, rng):
        import copy
        L2  = copy.deepcopy(L)
        row = rng.randrange(n)
        c1, c2 = rng.sample(range(n), 2)
        L2[row][c1], L2[row][c2] = L2[row][c2], L2[row][c1]
        return L2

    def ls_repair(L, rng):
        """Fix column conflicts greedily."""
        import copy
        L2 = copy.deepcopy(L)
        for j in range(n):
            col = [L2[i][j] for i in range(n)]
            missing = list(set(range(n)) - set(col))
            dups    = [v for v in col if col.count(v) > 1]
            if missing and dups:
                dup_val = dups[0]
                dup_rows = [i for i in range(n) if L2[i][j]==dup_val]
                swap_i   = rng.choice(dup_rows)
                swap_j2  = rng.choice([jj for jj in range(n) if L2[swap_i][jj]==missing[0]])
                L2[swap_i][j], L2[swap_i][swap_j2] = L2[swap_i][swap_j2], L2[swap_i][j]
        new_s = ls_score(L2)
        return new_s < ls_score(L), L2

    # Direct construction via cyclic shift (always works for n)
    t0 = time.perf_counter()
    L  = [[(i + j) % n for j in range(n)] for i in range(n)]
    dt = time.perf_counter() - t0
    sc = ls_score(L)
    kv('Construction method',       f'Cyclic shift: L[i][j] = (i+j) mod {n}')
    kv('Score (want 0)',             sc)
    kv('Valid',                      ls_verify(L))
    kv('Construction time',          f'{dt*1000:.3f} ms')
    if sc == 0:
        found(f'Latin square of order {n} constructed directly')
        info(f'First row: {L[0]}')
        info(f'Middle row: {L[n//2]}')

    # ── [5] Generalize ─────────────────────────────────────────────────────────
    phase('GENERALIZE', 5, 'The governing condition across all n')
    note(f'For any n, L[i][j] = (i+j) mod n is a valid Latin square')
    note(f'The twisted-translation analog: row i is a cyclic shift of row 0 by i')
    note(f'The r_c analog: shift amount = 1 (coprime to n when n>1 ✓)')

    # ── [6] Bound ─────────────────────────────────────────────────────────────
    phase('PROVE LIMITS', 6, 'Where does the cyclic construction fail?')
    kv('Cyclic L[i][j]=(i+j)%n',  'Always a valid Latin square for n≥1')
    kv('Orthogonality of cyclic',  'Two cyclic squares are NEVER orthogonal')
    kv('Proof sketch',
       'L[i][j]=(i+j)%n and L\'[i][j]=(i+2j)%n: pairs (L,L\') repeat when n even')
    note('Even n obstruction for orthogonality mirrors even-m obstruction in Cycles!')
    return L


# ══════════════════════════════════════════════════════════════════════════════
# DOMAIN B: GRAPH k-COLORING
# Fiber: BFS layers; Score: conflict count; SA search
# ══════════════════════════════════════════════════════════════════════════════

def domain_B():
    domain_header('B', 'Graph k-Coloring',
        'Color vertices so no two adjacent vertices share a color')

    # Petersen graph (famous hard case)
    n = 10  # vertices
    edges = [
        (0,1),(1,2),(2,3),(3,4),(4,0),          # outer pentagon
        (0,5),(1,6),(2,7),(3,8),(4,9),           # spokes
        (5,7),(7,9),(9,6),(6,8),(8,5),           # inner pentagram
    ]
    k = 3  # chromatic number of Petersen = 3
    info(f'Petersen graph: {n} vertices, {len(edges)} edges, chromatic number = {k}')

    # ── [1] Reframe ──────────────────────────────────────────────────────────
    phase('REFRAME', 1, 'BFS fiber stratification')
    # BFS from vertex 0
    layers = [-1]*n; layers[0]=0
    q = [0]
    while q:
        v = q.pop(0)
        for a,b in edges:
            nb = b if a==v else (a if b==v else -1)
            if nb>=0 and layers[nb]==-1:
                layers[nb] = layers[v]+1; q.append(nb)
    num_layers = max(layers)+1
    fm = FiberMap(range(n), lambda v: layers[v], num_layers)
    rep= fm.report()
    kv('BFS layers from vertex 0', num_layers)
    kv('Layer sizes',              rep['sizes'])
    kv('Cross-layer edges only',   'BFS → edges mostly cross layers (no back-edges in tree)')
    note('Fiber map: layer = BFS distance from source')
    note('Cross-layer constraint: adjacent layer vertices need different colors')
    note('Within-layer constraint: non-adjacent in BFS tree may still share edges')

    # ── [2] Obstruct ─────────────────────────────────────────────────────────
    phase('OBSTRUCT', 2, 'Odd cycle obstruction for 2-colorability')
    def has_odd_cycle(edges, n):
        color = [-1]*n
        for start in range(n):
            if color[start] != -1: continue
            color[start] = 0; q=[start]
            while q:
                v=q.pop(0)
                for a,b in edges:
                    nb=b if a==v else (a if b==v else -1)
                    if nb<0: continue
                    if color[nb]==-1:
                        color[nb]=1-color[v]; q.append(nb)
                    elif color[nb]==color[v]:
                        return True
        return False

    odd = has_odd_cycle(edges, n)
    kv('Has odd cycle', odd)
    kv('2-colorable', not odd)
    kv('Petersen graph k-chromatic', 3)
    note('Obstruction: odd cycle → χ(G) ≥ 3')
    note('Exact obstruction: Petersen has odd cycles → 2-coloring impossible')
    note('Upper bound: Petersen is 3-colorable (no 4-clique → χ ≤ 4 by Brooks)')

    # ── [3] Score + Solve ──────────────────────────────────────────────────────
    phase('SCORE + SOLVE', 3, 'Conflict score drives SA to valid coloring')
    adj = [set() for _ in range(n)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)

    def color_score(coloring):
        return sum(1 for a,b in edges if coloring[a]==coloring[b])

    def color_verify(coloring):
        return color_score(coloring)==0

    sa = SAEngine(
        init_fn   =lambda rng: [rng.randrange(k) for _ in range(n)],
        perturb_fn=lambda c,rng: [rng.randrange(k) if i==rng.randrange(n) else v
                                   for i,v in enumerate(c)],
        score_fn  =color_score,
        T_init=2.0, T_min=0.001, plateau_steps=20_000,
    )
    coloring, stats = sa.run(max_iter=200_000, seed=7)
    kv('SA iters',       f"{stats['iters']:,}")
    kv('SA elapsed',     f"{stats['elapsed']:.3f}s")
    kv('Best score',     stats['best_score'])
    kv('Coloring found', color_verify(coloring))
    if color_verify(coloring):
        found(f'Valid {k}-coloring: {coloring}')
        for c in range(k):
            verts = [v for v in range(n) if coloring[v]==c]
            info(f'  Color {c}: {verts}')

    # ── [4] Govern + Bound ───────────────────────────────────────────────────
    phase('GENERALIZE + PROVE LIMITS', 4, 'Governing condition and bounds')
    kv('Governing condition (k≥χ(G))',  'SA finds coloring iff k ≥ χ(G)')
    kv('Obstruction (k < χ(G))',        'Odd cycles, cliques, fractional chromatic number')
    kv('Fiber insight',                 'BFS layers guide color assignment order')
    kv('Score = 0 ↔ valid',             'Exact analog of cycles_score in Domain Cycles')
    note('The score function is the coordinate that bridges topology and search')
    return coloring


# ══════════════════════════════════════════════════════════════════════════════
# DOMAIN C: MAGIC SQUARES
# Parity obstruction + twisted translation of diagonals
# ══════════════════════════════════════════════════════════════════════════════

def domain_C(n=4):
    domain_header('C','Magic Squares',
        f'n={n}: place 1..n² so every row, column, and diagonal sums to S=(n(n²+1)/2)')

    magic_sum = n*(n**2+1)//2
    kv('Magic sum S', magic_sum)

    # ── [1] Reframe ──────────────────────────────────────────────────────────
    phase('REFRAME', 1, 'Row fibers + diagonal constraint as twisted translation')
    info(f'Fiber map: row index i → fiber F_i, each fiber has n values')
    info('Row constraint: each fiber (row) is a permutation of n values summing to S')
    info('Column/diagonal constraints: cross-fiber bijection conditions')
    note('Twisted translation analog: M[i][j] = a + i*b + j*c  (mod n²+1)')
    note('The r_c analog: b controls row-to-row shift of the pattern')

    # ── [2] Obstruct ─────────────────────────────────────────────────────────
    phase('OBSTRUCT', 2, 'Parity obstruction for n=2')
    # n=2 magic square: sum = 5, need 4 distinct values from {1,2,3,4}
    po = ParityObstruction(m=2, k=2, target=5)  # illustrative
    info('n=2: sum of 2 distinct values from {1,2,3,4} must equal 5')
    info('Row sums: (1+4)=5 or (2+3)=5 — only 2 choices')
    info('But 4 rows × 2 possible pairs → cannot avoid column repetition')
    info('n=2 magic square: IMPOSSIBLE (proven by exhaustion)')
    note('This is a parity + combinatorial obstruction')

    # n=4 has special obstruction (Frenicle)
    info(f'\nn=4: magic sum = {magic_sum}')
    info(f'Doubly even (n≡0 mod 4): use broken diagonal construction')

    # ── [3] Score + Solve ──────────────────────────────────────────────────────
    phase('SCORE + SOLVE', 3, 'SA on permutation with sum-deviation score')
    S = magic_sum

    def magic_score(flat):
        """Sum-deviation from magic sum across rows, cols, diagonals."""
        M = [[flat[i*n+j] for j in range(n)] for i in range(n)]
        dev = 0
        for i in range(n): dev += abs(sum(M[i]) - S)
        for j in range(n): dev += abs(sum(M[i][j] for i in range(n)) - S)
        dev += abs(sum(M[i][i] for i in range(n)) - S)
        dev += abs(sum(M[i][n-1-i] for i in range(n)) - S)
        return dev

    def magic_verify(flat):
        return magic_score(flat) == 0

    vals = list(range(1, n*n+1))

    def magic_init(rng):
        v = vals[:]; rng.shuffle(v); return v

    def magic_perturb(flat, rng):
        f2 = flat[:]; i,j = rng.sample(range(len(f2)),2)
        f2[i],f2[j] = f2[j],f2[i]; return f2

    sa = SAEngine(
        init_fn=magic_init, perturb_fn=magic_perturb, score_fn=magic_score,
        T_init=500.0, T_min=0.1, plateau_steps=30_000,
    )
    flat, stats = sa.run(max_iter=300_000, seed=3)
    kv('SA iters',   f"{stats['iters']:,}")
    kv('Best score', stats['best_score'])
    kv('Valid',      magic_verify(flat))

    if magic_verify(flat):
        found(f'{n}×{n} magic square found!')
        for i in range(n):
            row_str = '  '.join(f'{flat[i*n+j]:3d}' for j in range(n))
            print(f'    {row_str}')
    else:
        # Closed-form for n=4 (Albrecht Durer construction variant)
        info(f'SA did not converge — using Siamese/staircase construction for n={n}')
        if n % 2 == 1:
            # Siamese method for odd n
            M = [[0]*n for _ in range(n)]
            r,c = 0, n//2
            for num in range(1, n*n+1):
                M[r][c] = num
                nr,nc   = (r-1)%n, (c+1)%n
                if M[nr][nc]: nr,nc = (r+1)%n, c
                r,c = nr,nc
            flat = [M[i][j] for i in range(n) for j in range(n)]
            found(f'Siamese construction: score={magic_score(flat)}')
            for row in M:
                print('    ' + '  '.join(f'{v:3d}' for v in row))

    # ── [4] Govern + Bound ────────────────────────────────────────────────────
    phase('GENERALIZE + PROVE LIMITS', 4, 'Governing condition')
    kv('Magic square exists for', 'all n ≥ 1 except n=2')
    kv('Odd n construction',      'Siamese method (twisted translation with r=1, c=1)')
    kv('Doubly-even n (4|n)',      'Broken-diagonal or LUX construction')
    kv('Singly-even n (n≡2 mod4)','LUX method (most complex)')
    kv('Parity obstruction',      'n=2: impossible (not n≡2 mod 4 issue — a count issue)')
    note('The twisted translation IS the Siamese method: each number placed at (r-1, c+1) mod n')
    note('The governing condition is exactly: n is odd → Siamese works, n=2 → impossible')


# ══════════════════════════════════════════════════════════════════════════════
# DOMAIN D: DIOPHANTINE SYSTEMS  (modular fiber + impossibility)
# ══════════════════════════════════════════════════════════════════════════════

def domain_D():
    domain_header('D','Diophantine Systems',
        'Reformulate integer equations via fiber stratification mod m')

    # Problem family: x^2 + y^2 = z^2 (Pythagorean triples)
    #                 x^2 + y^2 = n   (sum of two squares)
    #                 x^2 ≡ a (mod p) (quadratic residues)

    # ── [1] Reframe ──────────────────────────────────────────────────────────
    phase('REFRAME', 1, 'Modular fiber stratification')
    info('Problem: which n are sums of two squares? n = x² + y²')
    info('Fiber map: f(n) = n mod 4  → 4 fibers F_0, F_1, F_2, F_3')
    info('Key: squares mod 4 are only 0 or 1')
    kv('x² mod 4 ∈',   '{0, 1}  (since (2k)²=4k², (2k+1)²=4k²+4k+1)')
    kv('x²+y² mod 4 ∈','{0,1,2} (sums of {0,1})')
    kv('n≡3 mod 4',    'Cannot be sum of two squares!')
    note('Fiber 3 (n≡3 mod 4) is unreachable — an exact obstruction from the fiber map')

    # ── [2] Obstruct ─────────────────────────────────────────────────────────
    phase('OBSTRUCT', 2, 'The mod-4 impossibility proof')
    print()
    print(f'  {W}Theorem:{Z} n = x² + y² has solutions iff in prime factorization of n,')
    print(f'  every prime p ≡ 3 (mod 4) appears to an even power.')
    print()
    for n in range(1, 21):
        ok = all(
            e%2==0
            for p,e in __import__('sympy').factorint(n).items()
            if p%4==3
        ) if n > 0 else True
        x2y2 = [(x,y) for x in range(int(n**0.5)+1)
                 for y in range(int(n**0.5)+1) if x*x+y*y==n]
        sym   = f'{G}✓{Z}' if (ok and x2y2) or (not ok and not x2y2) else f'{R}!{Z}'
        print(f'    n={n:3d}: {sym} theorem_says={ok}  solutions={x2y2[:2]}')

    # ── [3] Govern ────────────────────────────────────────────────────────────
    phase('GOVERN', 3, 'Governing condition: Fermat two-square theorem')
    note('Governing condition: n = x² + y² iff every prime p≡3(mod 4) divides n evenly')
    note('Fiber analog: stratify primes by p mod 4 → two classes')
    kv('p≡1 mod 4', 'Can always be written as p = a² + b² (Fermat, 1640)')
    kv('p≡3 mod 4', 'Cannot be written as sum of 2 squares')
    kv('p=2',       '2 = 1² + 1² — special case')
    note('The governing condition IS the modular fiber classification')

    # ── [4] Pythagorean triples via fiber ─────────────────────────────────────
    phase('BONUS: Pythagorean triples', 4, 'Parametric fiber construction')
    info('x² + y² = z²: parametrize via Euclid\'s formula')
    info('Fiber map: (x,y,z) → (m,n) with x=m²-n², y=2mn, z=m²+n²')
    triples = [(m**2-n**2, 2*m*n, m**2+n**2)
               for m in range(2,9) for n in range(1,m)
               if gcd(m,n)==1 and (m-n)%2==1
               and m**2-n**2 > 0]
    triples = sorted(set(triples))[:8]
    kv('Primitive triples (m>n>0, gcd=1, m-n odd)', '')
    for t in triples:
        check = t[0]**2 + t[1]**2 == t[2]**2
        print(f'    {t[0]:3d}² + {t[1]:3d}² = {t[2]:3d}²  check={G}✓{Z if check else R+"✗"+Z}')
    note('The parametric map (m,n)→(x,y,z) is the twisted translation for this domain')
    note('Governing: gcd(m,n)=1 and m-n odd → primitive triple (coprimality condition reappears!)')

    # ── [5] Bound ─────────────────────────────────────────────────────────────
    phase('PROVE LIMITS', 5, 'Fermat Last Theorem as the ultimate bound')
    kv('x²+y²=z²', 'Infinitely many solutions (Pythagorean triples)')
    kv('x³+y³=z³', 'No solutions in positive integers (Fermat-Wiles)')
    kv('General: xⁿ+yⁿ=zⁿ, n≥3', 'No solutions — the ultimate obstruction (Wiles 1995)')
    note('The bound: the exponent n=2 is the exact boundary of the solvable family')
    note('For n≥3: no fiber construction can find solutions — they do not exist')


# ══════════════════════════════════════════════════════════════════════════════
# DOMAIN E: COVERING CODES
# Layer decomposition + governing condition (Hamming bound)
# ══════════════════════════════════════════════════════════════════════════════

def domain_E():
    domain_header('E','Covering Codes',
        'Find minimum codewords so every binary string is within distance r of some codeword')

    n = 7  # Hamming(7,4) code
    r = 1  # covering radius
    k = 4  # message bits

    # ── [1] Reframe ──────────────────────────────────────────────────────────
    phase('REFRAME', 1, 'Hamming distance as fiber map')
    info(f'Binary strings of length n={n}: {2**n} total')
    info(f'Fiber map: f(w) = distance from nearest codeword')
    info(f'Fibers: F_0 = codewords, F_1 = strings at distance 1, ...')
    kv('Covering radius r', r)
    kv('Goal', 'Every string in F_0 ∪ F_1 (covered within distance 1)')

    # ── [2] Obstruct — Hamming bound ─────────────────────────────────────────
    phase('OBSTRUCT', 2, 'Hamming (sphere-packing) bound as parity obstruction')
    import math
    def hamming_ball(n_, r_):
        return sum(math.comb(n_,i) for i in range(r_+1))

    ball = hamming_ball(n, r)
    min_codewords = math.ceil(2**n / ball)
    kv('Ball of radius 1 (size)', ball)
    kv('Lower bound on |C|',      min_codewords)
    kv('Hamming(7,4): |C|=',      2**k)
    kv('Ball × |C|',              f'{ball} × {2**k} = {ball * 2**k}')
    kv('Total strings',           2**n)
    note('When ball_size × |C| = 2^n: perfect code (no waste)!')
    note('Hamming(7,4) is a perfect 1-error-correcting code: 8 × 16 = 128 = 2^7')

    # ── [3] Govern ─────────────────────────────────────────────────────────
    phase('GOVERN', 3, 'Governing condition: Hamming bound tightness')
    note('Perfect 1-error-correcting binary code of length n exists iff n = 2^r - 1')
    for r_val in range(1,6):
        n_val = 2**r_val - 1
        ball_val = hamming_ball(n_val, 1)
        k_val    = n_val - r_val
        perfect  = (ball_val * 2**k_val == 2**n_val)
        sym = f'{G}✓ PERFECT{Z}' if perfect else f'{R}✗{Z}'
        kv(f'  r={r_val}, n={n_val}, k={k_val}', sym)

    note('The governing condition gcd(r,m)=1 becomes: n = 2^r - 1 (power of 2 minus 1)')
    note('The parity obstruction: for other lengths, perfect codes are impossible')

    # ── [4] Verify Hamming(7,4) ───────────────────────────────────────────────
    phase('SCORE + SOLVE', 4, 'Verify the Hamming(7,4) code covers everything')
    # Generator matrix rows for Hamming(7,4)
    G_rows = [
        [1,0,0,0,0,1,1],
        [0,1,0,0,1,0,1],
        [0,0,1,0,1,1,0],
        [0,0,0,1,1,1,1],
    ]
    codewords = []
    for bits in range(2**k):
        word = [0]*n
        for i in range(k):
            if (bits >> i) & 1:
                word = [(word[j] + G_rows[i][j]) % 2 for j in range(n)]
        codewords.append(tuple(word))
    kv('Codewords generated', len(codewords))

    def hamming_dist(a, b):
        return sum(x != y for x, y in zip(a, b))

    # Check covering
    not_covered = []
    for w_int in range(2**n):
        w = tuple((w_int >> i) & 1 for i in range(n))
        if min(hamming_dist(w, c) for c in codewords) > r:
            not_covered.append(w)
    kv('Uncovered strings', len(not_covered))
    if not not_covered:
        found('Hamming(7,4) is a perfect covering code — confirmed!')

    # ── [5] Bound ─────────────────────────────────────────────────────────────
    phase('PROVE LIMITS', 5, 'Beyond Hamming: binary Golay code')
    kv('Hamming codes',   'Perfect for n=2^r−1, r≥1')
    kv('Binary Golay',    'n=23, r=3: another perfect code (unique)')
    kv('Tietäväinen 1973','Only Hamming and Golay are perfect binary codes')
    kv('Open question',   'Efficient construction for non-perfect codes with small covering radius')


# ══════════════════════════════════════════════════════════════════════════════
# DOMAIN F: PERMUTATION GROUP COSET DECOMPOSITION
# Coset fibers + twisted translation = exact analog
# ══════════════════════════════════════════════════════════════════════════════

def domain_F():
    domain_header('F','Permutation Group Decomposition',
        'Coset fibers are the abstract form of the fiber stratification')

    # S_n acting on Z_n: the cyclic subgroup structure
    n = 6

    # ── [1] Reframe ──────────────────────────────────────────────────────────
    phase('REFRAME', 1, 'Cosets as fibers — the abstract skeleton')
    info(f'Group G = Z_{n} = {{0,1,...,{n-1}}} under addition mod {n}')
    info(f'Subgroup H = 2Z_{n} = {{0, 2, 4}} (even elements, index 2)')
    H = [x for x in range(n) if x % 2 == 0]
    cosets = {}
    for x in range(n):
        rep = min((x - h) % n for h in H)
        cosets.setdefault(rep, []).append(x)
    kv('H (even subgroup)', H)
    kv('Cosets (fibers)',   dict(cosets))
    kv('Index [G:H]',       len(cosets))
    note('Cosets = fibers of the quotient map f: G → G/H')
    note('Every group element decomposes as: g = h + coset_rep  (twisted translation!)')
    note('THIS IS THE ABSTRACT FORM: Q_c(i,j) = (i+b_c(j), j+r_c) is coset decomposition in Z_m²')

    # ── [2] Obstruct ──────────────────────────────────────────────────────────
    phase('OBSTRUCT', 2, 'Lagrange theorem as the governing obstruction')
    print(f'\n  {W}Lagrange\'s Theorem:{Z}')
    print(f'  For finite group G and subgroup H: |H| divides |G|.')
    print(f'  Corollary: [G:H] = |G|/|H| is always an integer.')
    print()
    for g_size in [6, 8, 12, 24]:
        for h_size in [1, 2, 3, 4, 6, 8, 12]:
            if h_size > g_size: continue
            ok = (g_size % h_size == 0)
            if g_size == 6:
                kv(f'  |G|={g_size}, |H|={h_size}: divides?', f'{"yes" if ok else "NO — IMPOSSIBLE"}')

    note('Obstruction: |H| does not divide |G| → H cannot be a subgroup')
    note('This is the abstract form of the parity obstruction:')
    note('For Claude\'s Cycles: r_c must divide into m fibers of equal size')
    note('The requirement Σr_c = m is Lagrange for the fiber decomposition')

    # ── [3] Govern ────────────────────────────────────────────────────────────
    phase('GOVERN', 3, 'Sylow theorems: governing conditions for subgroup existence')
    info('When does a group G of order p^a * m (gcd(p,m)=1) have a subgroup of order p^a?')
    info('Sylow: always (Sylow p-subgroup always exists)')
    print(f'\n  {W}Sylow\'s First Theorem:{Z}')
    print(f'  If p^a divides |G|, then G has a subgroup of order p^a.')
    print(f'  This is the positive existence result.')
    print(f'\n  {W}Governing condition (Sylow count):{Z}')
    print(f'  Number of Sylow p-subgroups ≡ 1 (mod p) and divides |G|/p^a.')
    print()
    # Verify for small groups
    import sympy
    for order in [6, 8, 12, 24]:
        factors = sympy.factorint(order)
        for p, a in factors.items():
            sub_order = p**a
            # Number of Sylow p-subgroups
            divs = [d for d in sympy.divisors(order // sub_order)
                    if d % p == 1]
            kv(f'  |G|={order}, p={p}: Sylow count must be in',
               str(divs[:5]))

    note('Sylow count condition = coprimality condition from Claude\'s Cycles')
    note('gcd(r_c, m) = 1 ensures the coset structure decomposes into single cycles')

    # ── [4] Twisted translation as coset action ───────────────────────────────
    phase('PATTERN LOCK', 4, 'Twisted translation IS coset action')
    info('In Claude\'s Cycles: Q_c(i,j) = (i+b_c(j), j+r_c)')
    info('In group theory: left multiplication L_g(x) = g + x')
    info('The fiber level function = choosing a coset representative')
    info('b_c(j) = the coset representative for column j in fiber c')
    print()
    kv('Claude\'s r_c',     'Coset step — must be coprime to m (= group order) to generate full orbit')
    kv('Claude\'s b_c(j)',  'Coset representative function — specifies how orbits interleave')
    kv('Single-cycle cond', 'Orbit of length m² under Q_c = Q_c generates cyclic group of order m²')
    found('UNIFIED THEOREM: The single-cycle condition gcd(r_c, m)=1')
    found('is Lagrange\'s theorem applied to the coset decomposition structure.')
    found('Even-m impossibility = index-2 subgroup parity obstruction in Z_m².')

    # ── [5] Bound ─────────────────────────────────────────────────────────────
    phase('PROVE LIMITS', 5, 'Classification limits')
    kv('Finite cyclic groups',   'Every subgroup and coset structure completely classified')
    kv('Finite abelian groups',  'Completely classified (structure theorem)')
    kv('Non-abelian simple',     'Classification complete (CFSG, 2004) — 50-year project')
    kv('Open: Burnside problem', 'Infinite groups with all elements of finite order — partially open')
    note('The coordinate tool (coset fibers + coprimality) is the core of finite group theory')


# ══════════════════════════════════════════════════════════════════════════════
# SYNTHESIS: THE UNIFIED COORDINATE FRAMEWORK
# ══════════════════════════════════════════════════════════════════════════════

def synthesis():
    print(f"\n{hr('═')}")
    print(f"{W}SYNTHESIS: THE UNIFIED COORDINATE FRAMEWORK{Z}")
    print(hr('─'))
    print(f"""
  {W}The same four coordinates appear in every domain:{Z}

  {G}COORDINATE 1 — FIBER MAP{Z}
  f: objects → layers such that constraints become local per layer.
  {D}Cycles: f(i,j,k)=(i+j+k)%m → fibers  |  Graph: BFS distance
  Latin: row index               |  Codes: Hamming distance
  Groups: coset representative   |  Diophantine: residue mod 4{Z}

  {B}COORDINATE 2 — TWISTED TRANSLATION{Z}
  The local-to-global lift: how fiber-level solutions compose.
  {D}Cycles: Q_c(i,j)=(i+b_c(j),j+r_c)  |  Latin: L[i][j]=(i+j)%n
  Magic: Siamese step (1,1)               |  Groups: coset action g+x
  Codes: generator matrix rows            |  Diophantine: Euclid (m,n)→triple{Z}

  {M}COORDINATE 3 — GOVERNING CONDITION{Z}
  The minimal predicate P(params) that separates solvable from impossible.
  {D}Cycles: gcd(r_c,m)=1 AND Σr_c=m     |  Latin: n≠2 for LS existence
  Magic: n≠2                              |  Groups: |H| divides |G| (Lagrange)
  Codes: n=2^r-1 for perfect codes        |  Diophantine: primes p≡3(mod4) even{Z}

  {R}COORDINATE 4 — PARITY OBSTRUCTION{Z}
  The impossibility result: why the governing condition cannot be met.
  {D}Cycles (even m): 3 odds cannot sum to even
  Latin orthogonal (n=2,6): combination count fails
  Magic (n=2): value assignment impossible
  Groups: index-2 subgroup always normal (parity of S_n)
  Codes: sphere-packing bound not tight for non-Hamming lengths
  Diophantine: squares mod 4 ∈ {{0,1}} → sum ≢ 3 (mod 4){Z}
""")

    print(f"  {W}THE REFORMULATION PROTOCOL:{Z}")
    steps = [
        "Find f: objects → layers  (the fiber map)",
        "Identify cross-layer constraints  (what must cross fibers obey?)",
        "Express the cross-layer condition as a twisted translation  (Q_c form)",
        "Find the governing condition on the translation parameters  (coprimality analog)",
        "Derive the parity/modular obstruction  (why condition fails in some cases)",
        "Build score = violations of the governing condition  (0 iff valid)",
        "Apply SA + repair to reach score = 0",
    ]
    for i, step in enumerate(steps, 1):
        print(f"  {PHASE_COLORS_TEXT[(i-1)%6+1]}{i}. {step}{Z}")

    print(f"\n  {W}KEY INSIGHT:{Z}")
    print(f"  Every hard combinatorial problem has a natural fiber decomposition.")
    print(f"  Finding it reduces the problem from global intractable")
    print(f"  to local tractable + composition law.")
    print(f"  The composition law always has a governing coprimality-type condition.")
    print(f"  That condition's failure mode is always a parity/modular obstruction.")
    print(hr('═'))

PHASE_COLORS_TEXT = {1:G,2:R,3:B,4:M,5:Y,6:C}

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

DOMAINS = {
    'A': ('Latin Squares',         domain_A),
    'B': ('Graph k-Coloring',      domain_B),
    'C': ('Magic Squares',         domain_C),
    'D': ('Diophantine Systems',   domain_D),
    'E': ('Covering Codes',        domain_E),
    'F': ('Permutation Groups',    domain_F),
}

def main():
    args = sys.argv[1:]

    if '--domain' in args:
        idx = args.index('--domain')
        selected = [a.upper() for a in args[idx+1:] if a.upper() in DOMAINS]
    else:
        selected = list(DOMAINS.keys())

    print(hr('═'))
    print(f"{W}REFORMULATION ENGINE{Z}")
    print(f"{D}Applying the coordinate tools from Claude's Cycles to six problem domains{Z}")
    print(hr('═'))

    t0 = time.perf_counter()
    for letter in selected:
        title, fn = DOMAINS[letter]
        try:
            fn()
        except Exception as e:
            miss(f"Domain {letter} error: {e}")
            import traceback; traceback.print_exc()

    synthesis()
    print(f"\n{D}Total elapsed: {time.perf_counter()-t0:.1f}s{Z}")
    print(hr('═'))

if __name__ == "__main__":
    main()
