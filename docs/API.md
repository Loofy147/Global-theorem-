# API Documentation

## core.py
core.py — Mathematical Foundations
====================================
Weights · Verifier · Solutions · Level Machinery · SA Engine

The 8 weights classify any (m, k) problem in the moduli space M_k(G_m).
All are closed-form, all O(m²) or faster.

  W1  H² obstruction    bool   proves impossible in O(1)
  W2  r-tuple count     int    how many construction seeds
  W3  canonical seed    tuple  the direct construction path
  W4  H¹ order EXACT    int    phi(m)  — gauge multiplicity
  W5  search exponent   float  log₂(compressed space)
  W6  compression ratio float  W5 / log₂(full space)
  W7  solution lb       int    phi(m) × coprime_b(m)^(k-1)  [exact for m=3]
  W8  orbit size        int    m^(m-1)

Derivation of W4 = phi(m):
  |coprime-sum cocycles b: Z_m→Z_m| = m^(m-1) · phi(m)
  |coboundaries|                     = m^(m-1)
  |H¹(Z_m, coprime-sum)|            = phi(m)

Closure lemma (proved for m=3, conjectured general):
  Given b₀,...,b_{k-2} with gcd(sum,m)=1, b_{k-1} is determined.
  Therefore W7 = phi(m) × coprime_b(m)^(k-1)  [exact for m=3].

### `class Weights`
No description.

#### `def Weights.strategy(self)`
No description.

#### `def Weights.solvable(self)`
No description.

#### `def Weights.summary(self)`
No description.

### `def extract_weights(m, k)`
Extract all 8 weights for problem (m,k). Cached.

### `def weights_table(m_range, k_range)`
No description.

### `def verify_sigma(sigma, m)`
Verify sigma: Z_m^k → S_k yields k directed Hamiltonian cycles.
Checks: in-degree=1, components=1 for each color.

### `def table_to_sigma(table, m)`
Convert a list of level-dicts to the full sigma map.

### `def _level_valid(lv, m)`
No description.

### `def valid_levels(m)`
All valid level assignments for G_m. Cached.

### `def compose_Q(table, m)`
Compute the three composed fiber permutations Q_0, Q_1, Q_2.

### `def is_single_cycle(Q, m)`
No description.

### `def _build_sa(m, k)`
No description.

### `def _build_sa3(m)`
No description.

### `def _sa_score(sigma, arc_s, pa, n, k)`
No description.

### `def get_node_orbits(m, subgroup_generators)`
Identifies vertex orbits as flat indices. Supports arbitrary k.

### `def run_hybrid_sa(m, k, seed, max_iter, verbose)`
Hybrid discovery engine: alternates between Equivariant moves and Basin-repair.
Includes Basin Escape v3.1 logic with Basin-Burst.

### `def run_fiber_structured_sa(m, k, seed, max_iter, verbose, fiber_map_idx)`
SA where sigma(v) depends on (fiber(v), coords[1], ..., coords[k-2]).
Includes Basin Escape v3.1 logic for frontier breakages.
fiber_map_idx: index of the fiber map to use (0: sum, 1: i+2j+k, 2: 2i+j+k, 3: i+j+2k)

### `def get_canonical_spike_params(m, k)`
Returns the deterministic parameters for odd m or k=4, m=4.
r: shift triple/quadruple
v: base shift
delta: spike value
j0: spike position

### `def construct_spike_sigma(m, k)`
Directly construct a valid 3-Hamiltonian decomposition for any odd m.
Uses the discovered O(m) deterministic pattern:
- Step s=0: color 0 shifts j.
- Steps s=1..m-2: color 1 shifts j.
- Step s=m-1: color 2 shifts j.
- An i-shift is applied to one of the other colors based on (s, j).

### `def solve(m, k, seed)`
Unified solver. Returns sigma or None.
Routes: precomputed → geometric-construction → Hybrid SA.

## engine.py
No description.

### `class Domain`
No description.

#### `def Domain.__init__(self, name, n, k, m, fiber_map, tags, precomputed, group, notes)`
No description.

### `class Engine`
The Global Structure Engine provides a unified interface for classifying
and solving combinatorial problems using the Short Exact Sequence framework.

#### `def Engine.register(self, domain)`
No description.

#### `def Engine.print_results(self)`
No description.

#### `def Engine.__init__(self)`
No description.

#### `def Engine.run(self, m, k, strategy)`
Runs the classification and optional search for a problem (m, k).

Args:
    m: The group order (Z_m).
    k: The dimension (number of cycles).
    strategy: Search strategy ('standard', 'hybrid', 'equivariant').

Returns:
    A dictionary containing the status, proof steps, and solution if found.

#### `def Engine.analyse_text(self, desc, strategy)`
Automatically parses a text description and classifies the domain.

Args:
    desc: Text description of the problem.
    strategy: Search strategy to use.

#### `def Engine.simplify_problem(self, m, k)`
Uses categorical morphisms (Quotient, Product) to reduce a complex problem
to smaller solvable components.

#### `def Engine.get_lean_export(self, m, k)`
Generates Lean 4 source for the parity obstruction proof.

### `def get_suggested_morphisms(m, k)`
Suggests ways to simplify or solve (m, k) using known components.

### `def check_remote_search_status()`
Checks the status of Kaggle search kernels if CLI is configured.

## frontiers.py
frontiers.py — Open Problem Solvers
=====================================
P1  k=4, m=4  fiber-structured SA     (construction open)
P2  m=6, k=3  full-3D SA              (first attempts)
P3  m=8, k=3  full-3D SA              (harder)

TRIAGE FINDINGS (from recent measurements):
• P1 k=4 m=4: Score 337→230 in 300K iters of fiber-structured SA.
  Estimated budget: 4–8M iterations.
• P2 m=6 k=3: Basin-escape reaches score=4 in 8M iters (prev record 9).
  This is a deep local minimum (depth ≥ 3). Needs ~10M iters at T=2.0.
• P3 m=8 k=3: 512 vertices. Score function overhead scales linearly.

Run:
    python frontiers.py --p1        # k=4, m=4
    python frontiers.py --p2        # m=6, k=3
    python frontiers.py --p3        # m=8, k=3
    python frontiers.py --all       # all three
    python frontiers.py --status    # print current knowledge state

### `def found(s)`
No description.

### `def open_(s)`
No description.

### `def note(s)`
No description.

### `def hr(n)`
No description.

### `def solve_P1(max_iter, seeds, verbose)`
Find σ: Z_4^4 → S_4 such that each colour class is a Hamiltonian cycle.
Strategy: fiber-structured SA where σ(v) = f(fiber(v), j(v), k(v)).
The unique valid r-quadruple is (1,1,1,1) — all four colors share r_c=1.

MEASUREMENT: Score 337→230 in first 300K iterations.
K=4 converges ~4x slower than K=3. Estimated budget: 4–8M iterations.

### `def solve_P2(max_iter, seeds, verbose)`
G_6 has 216 vertices. Score function checks 3 components of 216 vertices.
Column-uniform impossible (parity). Full-3D search required.

### `def solve_P2_warm_start(max_iter, seed, verbose)`
m=6, k=3 warm-start approach using Z_3-lifted solution.

FINDING: The Z_3 lift (sigma_6(i,j,k) = sigma_3(i%3,j%3,k%3))
reaches score=9 reliably. This is a TRUE local minimum of depth >=3.
Escape requires ~10M iterations at T=2.0.

STRUCTURAL INSIGHT: Z_6 = Z_2 × Z_3 creates a product-structure
local minimum. Breaking it requires coordinated multi-vertex changes
that span the Z_3 periodic structure.

### `def solve_P3(max_iter, seeds, verbose)`
G_8: 512 vertices. Harder than m=6. Tests scaling.
Score function needs 512 components checked per iteration.

### `def print_status()`
No description.

### `def main()`
No description.

### `def prove_fiber_uniform_k4_impossible(verbose)`
THEOREM: No fiber-uniform σ yields a valid k=4 decomposition of G_4^4.
Proof method: exhaustive search over all 24^4 = 331,776 fiber-uniform sigmas.

Fiber-uniform means σ(v) depends only on fiber(v) = (i+j+k+l) mod 4.
With 4 fibers and 4 colors, there are 24^4 = 331,776 combinations.
This is small enough to check completely in ~40 seconds.

Result: 0 valid sigmas found → proved impossible.

## search.py
search.py — Three complementary search strategies for Claude's Cycles.

1. RANDOM SEARCH: Fast for odd m. Sample random valid-level combinations,
   check if Q compositions are single m²-cycles. Works well for m=3,5,7.

2. BACKTRACKING: Vertex-by-vertex with in-degree pruning. Explores the full
   sigma space (not restricted to column-uniform). Slower but more general.

3. SIMULATED ANNEALING: Continuous improvement via stochastic hill-climbing.
   Score = total "extra components" across 3 cycles (want 0).
   Effective at navigating large m.

All strategies return a SigmaTable (for fiber-based) or SigmaFn (for full 3D).

### `class RandomSearch`
Sample random combinations of valid level tables.
Extremely fast for odd m. Progressively slows for large m.

Usage:
    rs = RandomSearch(m=5)
    result = rs.run(max_attempts=50_000)

#### `def RandomSearch.__init__(self, m, seed)`
No description.

#### `def RandomSearch.attempts(self)`
No description.

#### `def RandomSearch.elapsed(self)`
No description.

#### `def RandomSearch.run(self, max_attempts)`
Return a valid SigmaTable or None if not found.

#### `def RandomSearch.run_verbose(self, max_attempts, report_every)`
Like run() but prints progress.

### `class BacktrackSearch`
Vertex-by-vertex assignment of sigma with pruning:
- Each cycle gets exactly one arc from each vertex (permutation = guaranteed).
- Each vertex has in-degree exactly 1 per cycle (checked incrementally).
- Optionally shuffles perm order (via seed) for different search trees.

Usage:
    bt = BacktrackSearch(m=3, seed=42)
    sigma_fn = bt.run()

#### `def BacktrackSearch.__init__(self, m, seed)`
No description.

#### `def BacktrackSearch.nodes_visited(self)`
No description.

#### `def BacktrackSearch.run(self)`
Return SigmaFn or None.

### `class SimulatedAnnealing`
Score = total number of extra cycle components (want 0).
Perturb: change sigma at one random vertex.
Temperature schedule: geometric cooling.

Usage:
    sa = SimulatedAnnealing(m=4, seed=0)
    sigma_fn = sa.run(max_iter=500_000)

#### `def SimulatedAnnealing.__init__(self, m, seed, T_init, T_min)`
No description.

#### `def SimulatedAnnealing.best_score(self)`
No description.

#### `def SimulatedAnnealing._score(self, funcs, m)`
Sum of extra components (0 = perfect).

#### `def SimulatedAnnealing.run(self, max_iter, verbose, report_every)`
No description.

#### `def SimulatedAnnealing.run_verbose(self, max_iter)`
No description.

### `def find_sigma(m, strategy, seed, max_iter, verbose)`
Find a valid sigma for the given m using the best available strategy.

strategy="auto":
  - odd m  → RandomSearch (fast, fiber-based)
  - even m → SimulatedAnnealing (full 3D)
strategy="random"    → RandomSearch only
strategy="backtrack" → BacktrackSearch only
strategy="sa"        → SimulatedAnnealing only

Returns SigmaFn or None.

## theorems.py
theorems.py — Theorems, Proofs, and the Moduli Theorem
=========================================================
Every result is stated, proved from weights, and verified computationally.

THEOREM INDEX
─────────────
Thm 3.2  Orbit-Stabilizer:     |Z_m³| = m × m²  for all m
Thm 5.1  Single-Cycle Conds:   Q_c is m²-cycle iff gcd(r,m)=1 AND gcd(Σb,m)=1
Thm 6.1  Parity Obstruction:   Even m, odd k → column-uniform impossible
Thm 7.1  Existence Odd m:      r-triple (1,m−2,1) valid for all odd m≥3
Thm 8.2  m=4 Decomposition:    Explicit verified σ (64 vertices, 3 cycles)
Thm 9.1  k=4 Resolution:       (1,1,1,1) breaks even-m obstruction for m=4
Cor 9.2  Parity Classification: even m: odd k obstructed, even k feasible
Thm 10.1 Fiber-Uniform:       k=4, m=4 impossible (331,776 cases checked)
Moduli   Torsor Structure:      M_k(G_m) is a torsor under H¹(Z_m,Z_m²)
W4       H¹ exact formula:      |H¹| = phi(m)  [not an approximation]
W7-lb    Solution lower bound:  phi(m) × coprime_b(m)^(k-1)  [exact m=3]
Closure  Lemma (m=3):           b_{k-1} determined by b_0,...,b_{k-2}
P5-obs   Non-abelian parity:    S_3/A_3=Z_2 obeys same law
P6-fiber Product groups:        Z_m×Z_n fiber quotient = Z_gcd(m,n)

### `def proved(s)`
No description.

### `def fail(s)`
No description.

### `def note(s)`
No description.

### `def build_proof(m, k, solution)`
Build a formal proof dict from weights (and optionally a solution).

### `def verify_k2_2d_solvable(m, trials)`
Check if k=2 2D graph G_m^2 is solvable for given m.

### `def check_spike_conditions(m)`
Analytically verify Theorem 11.1 conditions for odd m.

### `def verify_all_theorems(verbose)`
No description.

### `def print_cross_domain_table()`
Print the master theorem instantiated across 6 domains.

### `def compute_H1_classes(m)`
Compute H¹(Z_m, coprime-sum cocycles) by explicit coboundary enumeration.
Result: phi(m) cohomology classes, each of size m^(m-1).

This is the machinery behind the Moduli Theorem:
All solutions are related by coboundary gauge transformations.

### `def verify_m4_structure()`
Verify the structural properties of the m=4 SA solution:
- dep_i: σ depends on the i-coordinate
- dep_j: σ depends on the j-coordinate
- dep_k: σ depends on the k-coordinate
- column_uniform: False (confirmed by parity obstruction)
All permutations used: all 6 elements of S_3 appear.

## domains.py
domains.py — Domain Definitions and Extensions
================================================
All registered domains, including the new P5/P6 results.

Domains:
  Cycles G_m       k=3  m=3..9  (odd: solved, even: partial)
  Cycles k=4       m=4,8        (arithmetic feasible)
  Latin squares                 (cyclic construction)
  Hamming codes                 (perfect covering)
  Difference sets               (design theory)
  P5: S_3 (non-abelian)        NEW: parity law extends
  P6: Z_m×Z_n                  NEW: fiber quotient = Z_gcd(m,n)

### `def proved(s)`
No description.

### `def open_(s)`
No description.

### `def note(s)`
No description.

### `def analyse_magic_squares(verbose)`
Magic squares via Siamese method — same fiber/twisted-translation structure.

### `def analyse_pythagorean(verbose)`
Pythagorean triples — fiber quotient Z_4, obstruction p≡3(mod4).

### `def _load_magic_pythagorean(engine)`
No description.

### `class DecompositionCategory`
Category of symmetric decomposition problems.
Objects = problems (G,k,φ). Morphisms = structure-preserving maps.
Eilenberg: a functor from {symmetric systems} → {cohomology theories}.

#### `def DecompositionCategory.__init__(self)`
No description.

#### `def DecompositionCategory.add_object(self, name, G, k, m, status, H1)`
No description.

#### `def DecompositionCategory.add_morphism(self, src, tgt, kind, desc)`
No description.

#### `def DecompositionCategory.print_category(self)`
No description.

### `def build_decomposition_category()`
No description.

### `def _load_heisenberg(engine)`
No description.

### `def load_all_domains(engine)`
No description.

### `def _load_cycles(engine)`
No description.

### `def _load_classical(engine)`
No description.

### `def analyse_P5_nonabelian(verbose)`
S_3 Cayley graph analysis.

RESULT (proved):
• SES:  0 → A_3 → S_3 → Z_2 → 0  is valid (A_3 normal, index 2)
• k=2 arc types: r-pair (1,1) sums to |Z_2|=2 ✓ → FEASIBLE
• k=3 arc types: no r-triple sums to 2 from {1} → OBSTRUCTED
• Same parity law as abelian case

DIFFERENCE from abelian:
• Twisted translation = conjugation Q_c(h) = g_c⁻¹·h·g_c
• H¹ gauge group = H¹(G/H, Z(H)) — involves centre of H
• A_3 is abelian, so Z(A_3)=A_3 and the gauge structure is the same

### `def _load_P5_nonabelian(engine)`
No description.

### `def analyse_P6_product_groups(verbose)`
Z_m × Z_n analysis.

RESULT (proved):
• Fiber map: φ(i,j) = (i+j) mod gcd(m,n)
• SES: 0 → ker(φ) → Z_m×Z_n → Z_gcd(m,n) → 0
• Governing condition uses gcd(m,n) as modulus
• Same parity obstruction formula with m replaced by gcd(m,n)

Examples:
• Z_4×Z_6: gcd=2 → k=3 OBSTRUCTED (same as G_2^n)
• Z_6×Z_9: gcd=3 → k=3 feasible (same as G_3^n)
• Z_3×Z_5: gcd=1 → trivial fiber (always feasible)

### `def _load_P6_product(engine)`
No description.

## fiber.py
fiber.py — Fiber decomposition of the Claude's Cycles problem.

KEY INSIGHT: The map  f(i,j,k) = (i+j+k) mod m  stratifies the digraph
into m "fiber" layers F_0, …, F_{m-1}, each of size m².
Every arc goes from F_s to F_{s+1 mod m}.

In fiber coordinates (i,j) with k = (s-i-j) mod m, the 3 arc types become:
  arc 0: (i,j) in F_s  →  (i+1, j)    in F_{s+1}   [shift (1,0)]
  arc 1: (i,j) in F_s  →  (i,   j+1)  in F_{s+1}   [shift (0,1)]
  arc 2: (i,j) in F_s  →  (i,   j)    in F_{s+1}   [shift (0,0) — identity]

A "column-uniform" sigma depends only on (s, j) — not on i.
At each level s, column j gets a fixed permutation: perm[j] = [arc→cycle].

The COMPOSED permutation after all m levels:
  Q_c(i,j) = (i + b_c(j),  j + r_c) mod m
where r_c = total j-increment for cycle c, b_c(j) = total i-increment.

Single m²-cycle condition:  gcd(r_c, m) = 1  AND  gcd(Σ b_c(j), m) = 1

### `def is_bijective_level(level, m)`
Check that at level s, each cycle c induces a bijection on Z_m².
For cycle c: the set of targets {(i+di, j+dj) : j in Z_m, i in Z_m}
must be exactly Z_m² (all m² positions hit).

### `def all_valid_levels(m)`
Enumerate all column-uniform level assignments that are bijective.

### `def compose_levels(sigma_table, m)`
Compose all m fiber-level functions to get Q_0, Q_1, Q_2.
Returns 3 permutations on Z_m² (as dicts).

### `def is_single_q_cycle(Q, m)`
Check that permutation Q on Z_m² is a single m²-cycle.

### `def table_to_sigma_fn(sigma_table, m)`
Convert a SigmaTable (indexed by [s][j]) into a 3D sigma function
sigma(i, j, k) that can be used with core.verify_sigma.
The key: depends only on s=(i+j+k)%m and j.

### `def analyze_Q_structure(Qs, m)`
Analyze whether Q_c has the twisted translation form:
  Q_c(i,j) = (i + b_c(j),  j + r_c) mod m
Returns a dict with r_c, b_c, is_twisted, single_cycle per cycle.

### `def verify_single_cycle_conditions(r_c, b_c, m)`
Verify the two necessary and sufficient conditions for Q_c to be a
single m²-Hamiltonian cycle.

### `def even_m_impossibility_check(m)`
Verify the impossibility theorem for even m:
No (r_0,r_1,r_2) with gcd(r_c,m)=1 can sum to m when m is even.

## research/tgi_core.py
No description.

### `class TGICore`
The heartbeat of Topological General Intelligence (TGI).

#### `def TGICore.__init__(self, m, k)`
No description.

#### `def TGICore.set_topology(self, m, k)`
Changes the current topological domain.

#### `def TGICore.reflect(self)`
Topological Reflection: Explains the current state manifold in natural language.

#### `def TGICore.reason_on(self, data)`
Routes and reasons over arbitrary data using the TGI-Parser.

#### `def TGICore.reasoning_path(self)`
No description.

#### `def TGICore.solve_manifold(self, max_iter)`
Finds the global structure (Hamiltonian decomposition) with Basin Escape feedback.

#### `def TGICore.lift_path(self, sequence, color)`
No description.

#### `def TGICore.measure_intelligence(self)`
No description.

## research/tlm.py
No description.

### `class TopologicalLanguageModel`
The Topological Language Model (TLM) with Path Lifting and Coordinate Mapping.

#### `def TopologicalLanguageModel.__init__(self, m, k)`
No description.

#### `def TopologicalLanguageModel.tokenize(self, text)`
Maps arbitrary text tokens to Z_m coordinates via hashing.

#### `def TopologicalLanguageModel._ensure_sigma(self)`
No description.

#### `def TopologicalLanguageModel.topological_attention(self)`
W4 Gauge Multiplicity acts as the 'attention breadth'.

#### `def TopologicalLanguageModel.generate(self, seed_text, length)`
Generates completion using Hamiltonian path lifting.

## research/tgi_parser.py
No description.

### `class TGIParser`
The TGI-Parser: Maps datasets, languages, and math to topological parameters (m, k).

#### `def TGIParser.__init__(self)`
No description.

#### `def TGIParser.parse_input(self, data)`
Detects content type and routes to the correct TGI core.

#### `def TGIParser._route(self, domain, raw_data)`
No description.

## research/tgi_agent.py
No description.

### `class TGIAgent`
The High-Level Topological General Intelligence (TGI) Agent.

#### `def TGIAgent.__init__(self)`
No description.

#### `def TGIAgent.query(self, data)`
Processes a query through the full TGI pipeline.

## KnowledgeMapper (research/knowledge_mapper.py)
Implements the Universal Ontology Mapper (Project ELECTRICITY logic).
- **m=256, k=4**: Default grid sizing for high-resolution mapping.
- **ingest_concept(category, name, payload)**: Maps a concept to a unique coordinate using Closure Hashing.
- **ingest_color(name, r, g, b, a)**: Natively embeds RGBA colors as topological coordinates.
- **map_relation(name_a, name_b, relation_type)**: Calculates the geometric trajectory (vector) between two concepts in the knowledge manifold.

## TGI Agent Enhancements (research/tgi_agent.py)
- **ingest_knowledge(category, name, payload)**: High-level interface for ontology mapping.
- **forge_relation(name_a, name_b, relation_type)**: Creates a topological link between concepts.
- **cross_reason(data_list)**: Synthesizes a comparative analysis of multiple topological manifolds.

## TensorFibrationMapper (research/tensor_fibration.py)
Lifts continuous neural weights into discrete topological manifolds.
- **m=255, k=3**: Optimized for odd m to ensure Hamiltonian solvability.
- **lift_layer(weights)**: Quantizes weights and projects them into ^k$, returning topological entropy and point distribution.
- **calculate_topological_entropy(weights)**: Measures the complexity of the neural-manifold projection.

## GroupExtension & Tower (algebraic.py)
Formal algebraic tools for Core B (Fibration Navigation).
- **GroupExtension(G_order, Q_order)**: Defines an SES -bash \to H \to G \to Q \to 0$.
- **Tower(orders)**: Creates a hierarchy of extensions for deep lifting.
- **lift_sequence(states)**: Maps a sequence of fiber states to a global coordinate.
- **project_sequence(g_state)**: Decomposes a global state into its constituent fibers.

## HierarchicalTLM (research/hierarchical_tlm.py)
Linguistic scale-up via semantic towers.
- **m, k, depth**: Default depth=2 for base, semantic, and structural fibers.
- **generate_hierarchical(seed, length)**: Generates text by navigating a formal algebraic tower of manifolds.
