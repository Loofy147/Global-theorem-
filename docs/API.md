# API Documentation

## aimo_3_gateway.py
Gateway notebook for https://www.kaggle.com/competitions/ai-mathematical-olympiad-progress-prize-3

### `class AIMO3Gateway`
Gateway class for the AI Mathematical Olympiad Progress Prize 3.
Provides the interface between the competition platform and the TGI solver.

#### `def AIMO3Gateway.__init__(self, data_paths)`
Initializes the AIMO gateway with data paths and sets a generous timeout.

Args:
    data_paths (tuple[str] | None): Tuple containing the test CSV path.

#### `def AIMO3Gateway.unpack_data_paths(self)`
Unpacks the provided data paths or uses default competition paths.

#### `def AIMO3Gateway.generate_data_batches(self)`
Generates batches of test data for evaluation.

Returns:
    Generator[tuple[pl.DataFrame, pl.DataFrame], None, None]: Batches of (row, row_id).

#### `def AIMO3Gateway.competition_specific_validation(self, prediction_batch, row_ids, data_batch)`
Performs competition-specific validation on predictions.

## algebraic.py
No description.

### `class AlgebraicClassifier`
Classifies symmetric combinatorial problems in O(1) using cohomology.
Guided by Law I (Dimensional Parity Harmony) and Law V (Joint-Sum Constraint).
Determines existence of Hamiltonian paths in Z_m^k.

#### `def AlgebraicClassifier.__init__(self, m, k)`
Initializes the classifier with grid modulus m and dimensionality k.

Args:
    m (int): The grid modulus (number of levels per dimension).
    k (int): The dimensionality of the manifold.

#### `def AlgebraicClassifier.analyze(self)`
Performs a deep audit of the topological domain and returns a formal proof.

Returns:
    Dict[str, Any]: Proof metadata including existence, theorem ID, and proof steps.

### `class GroupExtension`
Formalizes the Short Exact Sequence 0 -> H -> G -> Q -> 0.
Enables decomposition of G into fiber H and quotient Q.

#### `def GroupExtension.__init__(self, G_order, Q_order)`
Initializes the extension with global order G and quotient order Q.

#### `def GroupExtension.lift(self, q_state, h_state)`
Lifts a point from the quotient and fiber to the total space.

#### `def GroupExtension.project(self, g_state)`
Projects a point from the total space to the quotient and fiber.

### `class Tower`
A hierarchy of Group Extensions (Tower of Fibrations).
Enables deep cognitive mapping across multiple manifold layers.

#### `def Tower.__init__(self, orders)`
Initializes the tower with a list of orders [base, ..., total].

#### `def Tower.lift_sequence(self, states)`
Lifts a state through the entire tower from base to total space.

#### `def Tower.project_sequence(self, g_state)`
Decomposes a global state into its constituent fiber components across the tower.

### `class NonAbelianSubgroup`
Helper for subgroups with non-abelian central extensions.

#### `def NonAbelianSubgroup.__init__(self, G_order, H_order, is_central)`
Initializes the subgroup with global, fiber, and central metadata.

#### `def NonAbelianSubgroup.parity_law(self, k)`
Checks the finalized parity law for non-abelian extensions.

### `def analyze_advanced_domain(domain)`
Advanced classification for icosahedral, crystal, and Hamming geometries.

### `def get_algebraic_proof(m, k)`
Convenience wrapper for AlgebraicClassifier.analyze.

### `def get_heisenberg_proof(m, k)`
Analysis of Hamiltonian decomposition for Heisenberg groups H3(Z_m).

## analysis.py
analysis.py — Automated mathematical analysis of Claude's Cycles solutions.

Given a sigma function or SigmaTable, this module:

1. STRUCTURAL ANALYSIS
   - Detects column-uniformity (does sigma depend only on s,j or all of i,j,k?)
   - Computes the Q_c composed permutations
   - Identifies the twisted translation form Q_c(i,j) = (i+b_c(j), j+r_c)

2. THEOREM VERIFICATION
   - Theorem 1: Twisted Translation Structure (auto-detected)
   - Theorem 2: Single-Cycle Conditions (gcd checks)
   - Theorem 3: Existence for odd m (constructive verification)
   - Theorem 4: Impossibility for even m (parity argument)

3. PATTERN REPORTING
   - Full solution tables
   - Arc sequences for each Hamiltonian cycle
   - Comparison across m values

### `def detect_dependencies(sigma, m)`
Determine which coordinates sigma actually depends on.
Returns {'i': bool, 'j': bool, 'k': bool, 's': bool}
where s = (i+j+k) mod m.

### `def extract_sigma_table(sigma, m)`
If sigma is column-uniform (depends only on s,j), extract SigmaTable.
Returns None if sigma is not column-uniform.

### `class SolutionAnalysis`
Comprehensive analysis of a Claude's Cycles solution.

Usage:
    analysis = SolutionAnalysis(sigma_fn, m=5)
    analysis.run()
    print(analysis.report())

#### `def SolutionAnalysis.__init__(self, sigma, m)`
No description.

#### `def SolutionAnalysis.run(self)`
No description.

#### `def SolutionAnalysis.report(self, verbose)`
No description.

#### `def SolutionAnalysis.__repr__(self)`
No description.

### `def compare_across_m(results)`
Generate a comparison table across multiple m values.
results: {m: SolutionAnalysis}

## benchmark.py
benchmark.py — v2.0 vs Alternatives
=====================================
Measures six solvers across six problems.
Reports: correctness, time, proof capability, speedup.

Run:
    python benchmark.py           # default (m=3..6, all solvers)
    python benchmark.py --quick   # m=3..5 only
    python benchmark.py --w4      # W4 correction speedup only
    python benchmark.py --scaling # scaling analysis

### `class BResult`
No description.

#### `def BResult.row(self)`
No description.

### `def _build_score(m)`
No description.

### `def solver_v2(m, k)`
No description.

### `def solver_A0_random(m, budget)`
No description.

### `def solver_A1_SA(m, max_iter)`
No description.

### `def solver_A2_backtrack(m)`
No description.

### `def solver_A3_v1(m, k)`
v1.0 pipeline with O(m^m) W4.

### `def _build_score(m)`
Helper: build integer-array score function.

### `def solver_A4_level_enum(m)`
Deterministic level enumeration. No randomness.
Occasionally faster than v2 on easy feasible problems (lucky early branch).
Cannot prove impossibility — times out on impossible problems.

### `def solver_A5_scipy(m)`
scipy Nelder-Mead on the discrete score function treated as continuous.
Included to document that gradient-free continuous optimization fails
completely on discrete problems. Always returns 0/N correct.

### `def run_benchmark(problems, verbose)`
No description.

### `def print_summary(all_results, problems)`
No description.

### `def w4_benchmark()`
No description.

### `def main()`
No description.

## cli.py
cli.py — Command-line interface for the Claude's Cycles system.

Usage:
    python -m claudecycles                   # demo all modes
    python -m claudecycles verify 3          # verify known m=3 solution
    python -m claudecycles verify 5          # verify known m=5 solution
    python -m claudecycles solve 7           # find+verify m=7
    python -m claudecycles solve 9           # find+verify m=9
    python -m claudecycles analyze 3         # deep analysis of m=3
    python -m claudecycles theorem           # verify all four theorems
    python -m claudecycles compare 3 5 7     # compare solutions across m

All results are auto-verified before printing.

### `def cmd_verify(m)`
Verify a known hardcoded solution.

### `def cmd_solve(m, strategy, seed, max_iter)`
Find and verify a solution for given m.

### `def cmd_analyze(m)`
Deep mathematical analysis of a solution.

### `def cmd_theorem()`
Demonstrate and verify all four theorems.

### `def cmd_compare(m_values)`
Compare solutions across multiple m values.

### `def cmd_demo()`
Full demo: verify known solutions, analyze, run theorems.

### `def main(args)`
No description.

## core.py
core.py — Mathematical Foundations (Production Stable)
====================================
Weights · Verifier · Solutions · Level Machinery · SA Engine

### `class Weights`
No description.

#### `def Weights.strategy(self)`
No description.

#### `def Weights.summary(self)`
No description.

### `def _check_fso_solvability(m, r)`
The Non-Canonical Obstruction check: Joint sum constraint.

### `def extract_weights(m, k)`
No description.

### `def verify_sigma(sigma, m)`
No description.

### `def table_to_sigma(table, m)`
No description.

### `def _sa_score(sigma, arc_s, pa, n, k)`
No description.

### `def _build_sa(m, k)`
No description.

### `def run_hybrid_sa(m, k, seed, max_iter)`
No description.

### `def construct_spike_sigma(m, k)`
Sovereign Spike Construction (O(m)). Proven Golden Path for all odd m.

### `def solve(m, k, seed, max_iter)`
The Sovereign FSO Master Solver.

### `def repair_manifold(m, k, sigma_in, max_iter)`
No description.

### `def verify_basin_escape_success(m, k, sigma_in, max_iter)`
No description.

### `def build_functional_graphs(sigma, m)`
No description.

### `def verify_functional_graph(fg, m)`
No description.

### `def vertices(m, k)`
No description.

### `def trace_cycle(fg, m)`
No description.

### `def arc_sequence(path, m)`
No description.

## debug_m4.py
No description.

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

## find_m3.py
No description.

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

## generate_api_docs.py
No description.

### `def get_docstring(node)`
No description.

### `def format_args(args)`
No description.

### `def parse_file(filename)`
No description.

## kaggle_search.py
No description.

### `def _build_sa(m, k)`
No description.

### `def _sa_score(sigma, arc_s, pa, n, k)`
No description.

### `def get_node_orbits(m, k, subgroup_generators)`
No description.

### `def run_hybrid_sa(m, k, seed, max_iter, verbose)`
No description.

### `def run_fiber_structured_sa(m, k, seed, max_iter, verbose)`
No description.

### `def main()`
No description.

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

## solutions.py
solutions.py — Hardcoded verified solutions for Claude's Cycles.

All solutions have been computationally verified (3 Hamiltonian cycles).
Use get_solution(m) to retrieve; use construct_for_odd_m(m) for
a general algorithm that works on any odd m > 2.

### `def get_solution(m)`
Return a precomputed SigmaFn for known m values (currently m=3,5).
Returns None for unknown m (use search module instead).

### `def get_solution_table(m)`
Return the raw SigmaTable for known m values.

### `def known_m_values()`
Return sorted list of m values with hardcoded solutions.

### `def construct_for_odd_m(m, seed, max_attempts)`
Find a valid sigma for any odd m > 2 using RandomSearch.
The fiber decomposition approach always succeeds for odd m (Theorem 3).

Returns SigmaFn or None (None is unexpected for m ≤ ~15).

## test_basin.py
No description.

## test_sa.py
No description.

## theorems.py
theorems.py — Formal Verification of the SES Framework
========================================================
Verified theorems 3.2 through 17.1 (FSO Codex Laws I-XII).
Includes group actions, parity obstructions, and multi-modal fibrations.

### `def proved(s)`
No description.

### `def hr()`
No description.

### `def check_spike_conditions(m)`
Analytically verify Theorem 11.1 conditions for odd m.

### `def phi(n)`
No description.

### `def verify_moduli_space_laws()`
Verify Codex Laws II and III for m=3.

### `def verify_basin_escape_law()`
Verify Law VII (Basin Escape Axiom) for m=3.

### `def verify_cross_domain_consistency()`
Verify Law VIII (Multi-Modal Fibration Invariant).

### `def verify_subgroup_decomposition_law()`
Verify Law X (Recursive Subgroup Decomposition) for m=12.

### `def verify_symbolic_duality_law()`
Verify Law XI (Symbolic-Topological Duality).

### `def verify_hardware_hamiltonian_health()`
Verify Law IX (Hardware-Topological Equivalence).

### `def verify_all_theorems(verbose)`
No description.

### `def print_cross_domain_table()`
No description.

## research/action_mapper.py
No description.

### `class ActionMapper`
TGI Action-Coordinate Mapping.
Translates topological paths and coordinates into system-level 'Agentic' actions.
Ensures the TGI can 'do' things as a result of manifold reasoning.
Guided by Law VIII (Multi-Modal Consistency).

#### `def ActionMapper.__init__(self, m)`
No description.

#### `def ActionMapper.map_coord_to_action(self, coord)`
Maps a specific coordinate in Z_m^k to an action and its parameters.

#### `def ActionMapper.path_to_action_sequence(self, path)`
Converts a Hamiltonian path into a sequence of agentic actions.

#### `def ActionMapper.resolve_intent(self, intent_text)`
Lifts a textual intent into a coordinate for action execution.
Uses grounded TLM semantic mapping and Law VIII (Multi-Modal Consistency).

## research/admin_vision_process.py
No description.

### `def admin_process(image_path)`
No description.

## research/advanced_solvers.py
No description.

### `class GeneralCayleyEngine`
No description.

#### `def GeneralCayleyEngine.__init__(self, elements, op, gens, seed)`
No description.

#### `def GeneralCayleyEngine.score(self, sigma)`
No description.

#### `def GeneralCayleyEngine.solve(self, max_iter, verbose)`
No description.

### `class HeisenbergSolver`
No description.

#### `def HeisenbergSolver.__init__(self, m, seed)`
No description.

### `class TSPSolver`
No description.

#### `def TSPSolver.__init__(self, name, coords, seed)`
No description.

#### `def TSPSolver.score(self, tour)`
No description.

#### `def TSPSolver.nearest_neighbor(self)`
No description.

#### `def TSPSolver.solve(self, max_iter, init_method, verbose)`
No description.

### `def load_tsplib_instances(csv_path)`
No description.

## research/agentic_action_engine.py
No description.

### `class ActionExecutor`
TGI Action Executor (Phase 8 Completion).
Handles real execution of agentic plans and establishes the feedback loop.
Guided by Law VII (Basin Escape) and Law IX (Hardware Grounding).

#### `def ActionExecutor.__init__(self)`
No description.

#### `def ActionExecutor.execute_step(self, step)`
Executes a single step of an agentic plan.

#### `def ActionExecutor.execute_plan(self, plan)`
Executes a full multi-step plan and returns the audit trail.

### `class TopologicalActionEngine`
TGI Agentic Action Engine.
Executes and resolves multi-step topological paths into coherent agentic plans.

#### `def TopologicalActionEngine.__init__(self)`
No description.

#### `def TopologicalActionEngine.resolve_path_to_plan(self, path, base_intent)`
Resolves a sequence of coordinates into a multi-step execution plan.

## research/agentic_bridge.py
No description.

### `class AgenticBridge`
The TGI Agentic Bridge (Upgraded v4).
Links the topological action space to actual MCP tool signatures and LIBRARY metadata.
Guided by the FSO Codex Law VIII (Multi-Modal Consistency).

#### `def AgenticBridge.__init__(self)`
No description.

#### `def AgenticBridge.resolve_intent(self, intent)`
Maps a natural language intent to a topological manifold and action set.

#### `def AgenticBridge.resolve_resource_for_action(self, action_data, domain_hint)`
Finds the most appropriate tool or library for a topological action.

#### `def AgenticBridge.generate_agentic_plan(self, intent)`
Creates a fully resolved agentic plan from a natural language intent.

## research/agentic_expansion_demo.py
No description.

### `def run_demo()`
No description.

## research/agentic_tgi_demo.py
No description.

### `def run_demo()`
No description.

## research/aimo_p7_solver.py
No description.

### `def count_f2024_values()`
f(m) + f(n) = f(m + n + mn)
f(n) = \sum a_p * v_p(n+1)
a_p = f(p-1) >= 1
Constraint: f(n) <= 1000 for n <= 1000.
Find number of values for f(2024) = h(2025) = 4*a_3 + 2*a_5.

## research/aimo_reasoning_engine.py
No description.

### `class AIMOReasoningEngine`
No description.

#### `def AIMOReasoningEngine.__init__(self)`
No description.

#### `def AIMOReasoningEngine.solve(self, problem_latex, problem_id)`
No description.

## research/aimo_recurring_parquet.py
No description.

## research/aimo_solver.py
No description.

### `def solve_alice_bob()`
No description.

### `def solve_functional_equation()`
No description.

### `def count_f2024_values()`
No description.

### `def solve_double_sum_floor()`
No description.

## research/aimo_submission_script.py
No description.

### `def get_answer(problem_id)`
No description.

## research/aimo_submit.py
No description.

## research/analysis.py
analysis.py — Automated mathematical analysis of Claude's Cycles solutions.

Given a sigma function or SigmaTable, this module:

1. STRUCTURAL ANALYSIS
   - Detects column-uniformity (does sigma depend only on s,j or all of i,j,k?)
   - Computes the Q_c composed permutations
   - Identifies the twisted translation form Q_c(i,j) = (i+b_c(j), j+r_c)

2. THEOREM VERIFICATION
   - Theorem 1: Twisted Translation Structure (auto-detected)
   - Theorem 2: Single-Cycle Conditions (gcd checks)
   - Theorem 3: Existence for odd m (constructive verification)
   - Theorem 4: Impossibility for even m (parity argument)

3. PATTERN REPORTING
   - Full solution tables
   - Arc sequences for each Hamiltonian cycle
   - Comparison across m values

### `def detect_dependencies(sigma, m)`
Determine which coordinates sigma actually depends on.
Returns {'i': bool, 'j': bool, 'k': bool, 's': bool}
where s = (i+j+k) mod m.

### `def extract_sigma_table(sigma, m)`
If sigma is column-uniform (depends only on s,j), extract SigmaTable.
Returns None if sigma is not column-uniform.

### `class SolutionAnalysis`
Comprehensive analysis of a Claude's Cycles solution.

Usage:
    analysis = SolutionAnalysis(sigma_fn, m=5)
    analysis.run()
    print(analysis.report())

#### `def SolutionAnalysis.__init__(self, sigma, m)`
No description.

#### `def SolutionAnalysis.run(self)`
No description.

#### `def SolutionAnalysis.report(self, verbose)`
No description.

#### `def SolutionAnalysis.__repr__(self)`
No description.

### `def compare_across_m(results)`
Generate a comparison table across multiple m values.
results: {m: SolutionAnalysis}

## research/autonomous_engine_demo.py
No description.

### `def run_demo()`
No description.

## research/classify_new_domains.py
No description.

## research/collect_all_results.py
No description.

### `def get_stats(kernel_id)`
No description.

### `def main()`
No description.

## research/cycles_even_m.py
cycles_even_m.py — 6-Phase Discovery: Even m in Claude's Cycles
================================================================
The digraph G_m:  vertices (i,j,k) ∈ Z_m³
  arc 0: (i,j,k) → (i+1, j,   k  ) mod m
  arc 1: (i,j,k) → (i,   j+1, k  ) mod m
  arc 2: (i,j,k) → (i,   j,   k+1) mod m

sigma assigns each arc to one of 3 cycles.
Goal: every cycle is a single directed Hamiltonian cycle of length m³.

Odd m  → column-uniform sigma works (proven, m=3,5,7 solved).
Even m → column-uniform is PROVABLY impossible.
         This script discovers WHY and then FINDS a solution via SA.

Phases:
  01 GROUND TRUTH   — define verification; confirm odd m works
  02 DIRECT ATTACK  — attempt column-uniform on m=4; record exact failure
  03 STRUCTURE HUNT — prove the parity obstruction; characterise what even m needs
  04 PATTERN LOCK   — SA search for m=4; analyse the solution structure
  05 GENERALIZE     — test the discovered structure on m=6
  06 PROVE LIMITS   — complete theorem: odd proven, even found, open frontier stated

Run:
  python cycles_even_m.py            # full 6-phase run
  python cycles_even_m.py --fast     # skip m=6 search (saves ~2 min)

### `def hr(c, n)`
No description.

### `def sec(num, name, tag)`
No description.

### `def kv(k, v, ind)`
No description.

### `def found(msg)`
No description.

### `def miss(msg)`
No description.

### `def note(msg)`
No description.

### `def info(msg)`
No description.

### `def vertices(m)`
No description.

### `def build_funcs(sigma, m)`
No description.

### `def count_components(fg)`
No description.

### `def score(sigma, m)`
Excess components across 3 cycles (0 = valid).

### `def verify(sigma, m)`
Full verification: each cycle is exactly 1 Hamiltonian cycle.

### `def build_funcs_list(sigma, m)`
Build 3 mutable dicts.

### `def fiber_valid_levels(m)`
All column-uniform level assignments where each cycle is bijective on Z_m².

### `def _cartesian(lst, k)`
No description.

### `def _level_bijective(level, m)`
No description.

### `def compose_q(table, m)`
Compose all m fiber levels → 3 permutations Q_c on Z_m².

### `def q_is_single_cycle(Q, m)`
No description.

### `def table_to_sigma(table, m)`
No description.

### `def find_odd_m(m, seed, max_att)`
No description.

### `def prove_column_uniform_impossible(m)`
Column-uniform needs r₀+r₁+r₂ = m, each gcd(rᵢ,m)=1.
For even m: coprime-to-m ⟹ odd. Sum of 3 odds is odd ≠ m (even). QED.
Returns dict with all proof data.

### `def exhaustive_column_uniform(m, max_combos)`
Try ALL column-uniform sigmas for small m. Record outcome.

### `def _build_perm_table(m)`
Precompute for each (vertex_idx, perm_idx) → [successor_0, s_1, s_2].
Returns succs[v][p][arc] = successor vertex index.

### `def _build_funcs_fast(sigma_int, arc_succ, perm_arc, n)`
Build 3 successor arrays from integer sigma.

### `def _count_comps_fast(f, n)`
Count cycle components in successor array.

### `def _score_fast(f0, f1, f2, n)`
No description.

### `def sa_search_fast(m, max_iter, T_init, T_min, seed, verbose, report_n)`
Fast SA with score=1 repair mode + plateau-escape reheat.
Returns (sigma_int_list or None, stats).

### `def _sigma_int_to_map(sigma_int, m)`
Convert integer sigma to SigmaMap.

### `def sa_multistart(m, restarts, iter_each, T_init, verbose)`
Multi-start SA. Return first success.

### `def analyse_sigma_dependencies(sigma, m)`
Find which coordinates sigma actually depends on.

### `def analyse_sigma_pattern(sigma, m)`
Analyse symmetry structure of a found sigma.

### `def analyse_q_structure(sigma, m)`
Extract Q_c (if sigma is column-uniform) or analyse fiber-level
transitions even for full-3D sigma.

### `def phase_01()`
No description.

### `def phase_02()`
No description.

### `def phase_03()`
No description.

### `def phase_04(fast)`
No description.

### `def phase_05(sigma4, fast)`
No description.

### `def phase_06(p4_result, p5_result)`
No description.

### `def main()`
No description.

## research/debug_spike_m3.py
No description.

## research/deploy_p1_fix.py
No description.

### `def deploy()`
No description.

## research/deploy_p2_p3.py
No description.

### `def deploy()`
No description.

## research/deploy_swarm.py
No description.

### `def deploy()`
No description.

## research/discovery_engine.py
discovery_engine.py — 6-Phase Mathematical Discovery Engine
============================================================
Pure sympy. No API. All six phases run as real computation.

Each phase applies one principle from the Discovery Methodology:
  01 GROUND TRUTH   — classify, parse, build the verifier
  02 DIRECT ATTACK  — try standard methods; record failures precisely
  03 STRUCTURE HUNT — factor, symmetry, decompose, find invariants
  04 PATTERN LOCK   — analyse the working answer; extract the law
  05 GENERALIZE     — parametrise the family; name the condition
  06 PROVE LIMITS   — find the boundary; state the obstruction

Usage:
  python discovery_engine.py "x^2 - 5x + 6 = 0"
  python discovery_engine.py "sin(x)^2 + cos(x)^2"
  python discovery_engine.py "factor x^4 - 16"
  python discovery_engine.py "x^3 - 6x^2 + 11x - 6 = 0"
  python discovery_engine.py "prove sqrt(2) is irrational"
  python discovery_engine.py "sum of first n integers"
  python discovery_engine.py "2x + 3 = 7"
  python discovery_engine.py --test       # run all built-in tests

### `def hr(char, n)`
No description.

### `def section(num, name, tagline)`
No description.

### `def kv(key, val, indent)`
No description.

### `def finding(msg, sym)`
No description.

### `def ok(msg)`
No description.

### `def fail(msg)`
No description.

### `def note(msg)`
No description.

### `class PT`
No description.

### `class Problem`
No description.

### `def _parse(s)`
No description.

### `def classify(raw)`
No description.

### `def phase_01(p)`
No description.

### `def phase_02(p, g)`
No description.

### `def phase_03(p, prev)`
No description.

### `def phase_04(p, prev)`
No description.

### `def phase_05(p, prev)`
No description.

### `def phase_06(p, prev)`
No description.

### `def _final_answer(p)`
No description.

### `def run(raw)`
No description.

### `def run_tests()`
No description.

## research/discovery_engine_unified.py
╔══════════════════════════════════════════════════════════════════════════════╗
║          DISCOVERY ENGINE  —  Complete Unified System                       ║
║          Finding Global Structure in Highly Symmetric Systems                ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT THIS FILE IS
─────────────────
A single self-contained system encoding every discovery, theorem, algorithm,
and search strategy produced during the Claude's Cycles investigation.
It is simultaneously:
  • The traceable record of what was found and how
  • The runnable proof of every theorem
  • The extended coordinate framework applicable to new domains
  • The improved search engine with structured SA

DISCOVERY ARC  (the strategic path that led here)
──────────────────────────────────────────────────
Phase 1  GROUND TRUTH    — verify() before search()
Phase 2  DIRECT ATTACK   — measure how failures fail
Phase 3  STRUCTURE HUNT  — the fiber map  f(v) = φ(v)
Phase 4  PATTERN LOCK    — twisted translation Q_c
Phase 5  GENERALIZE      — governing condition gcd(r_c,m)=1
Phase 6  PROVE LIMITS    — parity obstruction for even m

Extensions:
Ext 1    REFORMULATION   — same 4 coordinates in 6 domains
Ext 2    GLOBAL STRUCTURE — master theorem via SES
Ext 3    k=4 FRONTIER    — new theorem + structured search

THE FOUR COORDINATES  (the universal discovery tools)
───────────────────────────────────────────────────────
C1  Fiber Map           φ: G → G/H      (group quotient)
C2  Twisted Translation Q_c             (coset action on H)
C3  Governing Condition gcd(r_c,|G/H|)=1  (generator in G/H)
C4  Parity Obstruction  arithmetic of |G/H|  (when C3 fails)

Run:
    python discovery_engine_unified.py --demo          # full demo
    python discovery_engine_unified.py --cycles m=5    # solve G_m
    python discovery_engine_unified.py --verify        # verify all theorems
    python discovery_engine_unified.py --search k=4    # k=4 structured search
    python discovery_engine_unified.py --domains       # cross-domain analysis
    python discovery_engine_unified.py --strategy      # print strategy guide

### `def hr(c, n)`
No description.

### `def phase_header(n, name, tag)`
No description.

### `def proved(msg)`
No description.

### `def found(msg)`
No description.

### `def miss(msg)`
No description.

### `def note(msg)`
No description.

### `def info(msg)`
No description.

### `def kv(k, v)`
No description.

### `class FiberMap`
Universal fiber decomposition tool.

Given a group G (encoded as a list of elements) and a homomorphism
φ: G → Z_k, decompose G into k fibers F_0,...,F_{k-1}.

The short exact sequence:  0 → ker(φ) → G → Z_k → 0
is the algebraic skeleton of the decomposition.

Orbit-stabilizer theorem:  |G| = k × |ker(φ)|

#### `def FiberMap.__init__(self, elements, phi, k)`
No description.

#### `def FiberMap.verify_orbit_stabilizer(self)`
No description.

#### `def FiberMap.report(self)`
No description.

### `def cycles_fiber_map(m)`
No description.

### `class TwistedTranslation`
The induced action of a generator on the fiber H ≅ Z_m².

Q(i,j) = (i + b(j),  j + r)  mod m

This is the COSET ACTION: h ↦ h + g  (residual group action of g on H).

#### `def TwistedTranslation.__init__(self, m, r, b)`
No description.

#### `def TwistedTranslation.apply(self, i, j)`
No description.

#### `def TwistedTranslation.orbit_length(self)`
No description.

#### `def TwistedTranslation.is_single_cycle(self)`
No description.

#### `def TwistedTranslation.condition_A(self)`
gcd(r, m) = 1  ↔  r generates Z_m  ↔  j-shift has full period.

#### `def TwistedTranslation.condition_B(self)`
gcd(Σb(j), m) = 1  ↔  accumulated i-shift has full period.

#### `def TwistedTranslation.verify_theorem_5_1(self)`
THEOREM 5.1: Q is a single m²-cycle  iff  A and B both hold.
Returns verification dict with prediction vs actual.

#### `def TwistedTranslation.derivation_sketch(m)`
No description.

### `class GoverningCondition`
For a k-decomposition via the fiber structure, we need k parameters
r_0,...,r_{k-1} each coprime to m (generating G/H ≅ Z_m)
summing to m (the constraint from the identity action of arc type k-1).

This class analyses feasibility and finds valid r-tuples.

#### `def GoverningCondition.__init__(self, m, k)`
No description.

#### `def GoverningCondition.find_valid_tuples(self)`
No description.

#### `def GoverningCondition.canonical_tuple(self)`
The simplest valid tuple: (1, m-(k-1), 1, ..., 1) when feasible.

#### `def GoverningCondition.analyse(self)`
No description.

### `class ParityObstruction`
THEOREM 6.1 (Generalised):
For even m and odd k: no k-tuple from coprime-to-m elements can sum to m.
Proof: all such elements are odd; sum of k odd numbers has parity k%2;
       k odd → sum is odd; m is even → contradiction.

COROLLARY 9.2 (New):
k even → potentially feasible for all m.
The obstruction is k-parity specific, not m-parity specific.

#### `def ParityObstruction.__init__(self, m, k)`
No description.

#### `def ParityObstruction.analyse(self)`
No description.

#### `def ParityObstruction.complete_table(m_range, k_range)`
Generate the complete k×m feasibility table.

### `def _build_arc_succ_3(m)`
No description.

### `def _perm_table_3()`
No description.

### `def _build_funcs_3(sigma, arc_succ, perm_arc, n)`
No description.

### `def _count_comps(f, n)`
No description.

### `def _score_3(f0, f1, f2, n)`
No description.

### `def _level_bijective(level, m)`
No description.

### `def _valid_levels(m)`
No description.

### `def _compose_q(table, m)`
No description.

### `def _q_single(Q, m)`
No description.

### `def _table_to_sigma(table, m)`
No description.

### `def verify_sigma_map(sigma_map, m)`
Full verification of a sigma given as {(i,j,k): perm_tuple}.

### `class SAEngine3`
Fast SA for G_m (k=3) using integer arrays.
38K+ iterations/second on m=4.
Features: repair mode (score=1), plateau escape (reheat+reload).

#### `def SAEngine3.__init__(self, m)`
No description.

#### `def SAEngine3.run(self, max_iter, T_init, T_min, seed, verbose, report_n)`
No description.

### `class OddMSolver`
Column-uniform sigma via random level sampling.
Works for any odd m > 2 in expected polynomial time.

#### `def OddMSolver.__init__(self, m, seed)`
No description.

#### `def OddMSolver.solve(self, max_att)`
No description.

### `def find_sigma(m, seed, verbose)`
Unified solver: odd m → random fiber search; even m → SA.
Always returns {(i,j,k): perm_tuple} or None.

### `class SystemSpec`
Specifies a highly symmetric system for analysis.

name:        human-readable identifier
G_order:     |G|, the symmetry group order
H_order:     |H| = |ker(phi)|, the fiber size
k:           number of parts in decomposition
G_quotient:  |G/H| = k, the quotient group
governing:   string description of the governing condition
obstruction: string description of the impossibility case (or None)

#### `def SystemSpec.G_quotient(self)`
No description.

#### `def SystemSpec.verify_orbit_stabilizer(self)`
No description.

#### `def SystemSpec.report(self)`
No description.

### `class K4M4Engine`
Structured search for k=4, m=4.

The 4D digraph Z_4^4 (256 vertices, 4 arc types).
The fiber-uniform approach is PROVED IMPOSSIBLE (exhaustive: 24^4=331,776 checked).
The fiber-STRUCTURED approach restricts to σ(v) = f(fiber, j, k)
reducing the search from 24^256 to 24^64.

#### `def K4M4Engine.__init__(self)`
No description.

#### `def K4M4Engine._dec(self, v)`
No description.

#### `def K4M4Engine._enc(self, i, j, k, l)`
No description.

#### `def K4M4Engine._build_arc_succ(self)`
No description.

#### `def K4M4Engine._build_perm_arc(self)`
No description.

#### `def K4M4Engine._build_funcs(self, sigma)`
No description.

#### `def K4M4Engine._score(self, sigma)`
No description.

#### `def K4M4Engine.prove_fiber_uniform_impossible(self)`
Exhaustively check all 24^4 fiber-uniform sigmas.

#### `def K4M4Engine.sa_fiber_structured(self, max_iter, seed, verbose, report_n)`
SA in the fiber-structured subspace.
State: table[(s,j,k)] → perm_index, 64 entries, 24 choices each.
This is the correct restricted search space: σ(v) = f(fiber(v), j(v), k(v)).

### `def verify_all_theorems(verbose)`
Run all theorems as computational proofs.
Each theorem is stated, then verified by explicit computation.

### `def cross_domain_analysis()`
No description.

### `def print_strategy_guide()`
No description.

### `def cmd_demo()`
No description.

### `def cmd_cycles(m)`
No description.

### `def cmd_k4_search(fast)`
No description.

### `def main()`
No description.

## research/find_p1_params.py
No description.

### `def verify_k4(sigma, m)`
No description.

### `def solve_p1()`
No description.

## research/frontier_discovery.py
No description.

### `def _build_sa(m, k)`
No description.

### `def _sa_score(sigma, arc_s, pa, n, k)`
No description.

### `def get_node_orbits(m, k, generators)`
No description.

### `def run_frontier_sa(m, k, seed, max_iter, verbose)`
No description.

## research/global_structure.py
global_structure.py
===================
FINDING GLOBAL STRUCTURE IN HIGHLY SYMMETRIC SYSTEMS

The central theorem, proved and tested:

    For any combinatorial system with a transitive symmetry group G,
    every valid global decomposition is determined by:

        (1) A SUBGROUP CHAIN  H ⊴ G  (the fiber map is the quotient G → G/H)
        (2) AN INDUCED ACTION  of G/H on H  (the twisted translation)
        (3) A GENERATOR CONDITION  on the action parameters (coprimality analog)
        (4) A PARITY OBSTRUCTION  when the group arithmetic prevents (3)

    This is not a heuristic. It is orbit-stabilizer theorem + Lagrange's theorem
    applied to the action of G on the system's constraint graph.

We demonstrate this on five increasingly abstract systems:

    SYS 1: Claude's Cycles (Z_m³)         — the original, now understood fully
    SYS 2: Cayley graph of Z_n × Z_n      — 2D analog, different fiber structure
    SYS 3: Vertex-transitive graphs        — BFS fibers from group structure
    SYS 4: Affine planes AG(2,q)           — fiber = parallel class, q must be prime power
    SYS 5: Difference sets in Z_n          — the governing condition IS the multiplier theorem

The script:
  - Detects the symmetry group of each system
  - Predicts valid decompositions from group structure alone
  - Derives impossibility from arithmetic of group order
  - Verifies predictions computationally
  - Extracts the universal governing law

Run:
    python global_structure.py

### `def hr(c, n)`
No description.

### `def section(title, sub)`
No description.

### `def thm(label, statement)`
No description.

### `def proved(msg)`
No description.

### `def found(msg)`
No description.

### `def miss(msg)`
No description.

### `def note(msg)`
No description.

### `def info(msg)`
No description.

### `def kv(k, v)`
No description.

### `def step(n, msg)`
No description.

### `class AbelianGroup`
Finite abelian group  G = Z_{n1} × Z_{n2} × ... × Z_{nk}.
The key operations:
  - Subgroup enumeration (via divisors of each factor)
  - Quotient map construction
  - Orbit-stabilizer decomposition
  - Generator testing

#### `def AbelianGroup.__init__(self, *orders)`
No description.

#### `def AbelianGroup.elements(self)`
No description.

#### `def AbelianGroup.add(self, a, b)`
No description.

#### `def AbelianGroup.neg(self, a)`
No description.

#### `def AbelianGroup.zero(self)`
No description.

#### `def AbelianGroup.is_subgroup(self, H)`
No description.

#### `def AbelianGroup.cosets(self, H)`
No description.

#### `def AbelianGroup.subgroups_of_index(self, idx)`
Find all subgroups H with [G:H] = idx (i.e., |H| = |G|/idx).

#### `def AbelianGroup.generate(self, generators)`
Subgroup generated by a list of elements.

#### `def AbelianGroup.generator_order(self, g)`
Order of element g.

#### `def AbelianGroup.cyclic_generators(self)`
Elements that generate the full group (if cyclic).

#### `def AbelianGroup.is_cyclic(self)`
No description.

### `class FiberDecomposition`
Given group G and linear functional φ: G → Z_m (a group homomorphism),
decompose G into fibers F_s = φ⁻¹(s).

This is the ABSTRACT FORM of the Claude's Cycles fiber map.
The functional φ defines the 'stratification coordinate'.

#### `def FiberDecomposition.__init__(self, G, phi, num_fibers)`
No description.

#### `def FiberDecomposition.fiber_size(self)`
No description.

#### `def FiberDecomposition.cross_fiber_action(self, g)`
The induced action of g on fibers: maps F_s to F_{s + φ(g)}.
Within each fiber, the action is: h ↦ h + (g - φ(g) * e) projected to fiber.
This is the TWISTED TRANSLATION.

#### `def FiberDecomposition.verify_orbit_stabilizer(self)`
Verify: |G| = |orbit| × |stabilizer|
orbit = the set of fibers (size = num_fibers)
stabilizer = the kernel (size = fiber_size)

### `class TwistedTranslation`
The induced action Q on a single fiber F ≅ Z_m².

Q(i,j) = (i + b(j), j + r)  mod m

Parameters:
  r : the j-shift (= φ(generator), the 'fiber-crossing speed')
  b : the i-offset function (= residual i-component of generator)

Single-cycle condition:
  Q is a single m²-cycle iff:
    (A)  gcd(r, m) = 1
    (B)  gcd(Σ_j b(j), m) = 1

#### `def TwistedTranslation.__init__(self, m, r, b)`
No description.

#### `def TwistedTranslation.apply(self, i, j)`
No description.

#### `def TwistedTranslation.orbit_length(self)`
Length of the orbit of (0,0) under repeated application.

#### `def TwistedTranslation.is_single_cycle(self)`
No description.

#### `def TwistedTranslation.condition_A(self)`
No description.

#### `def TwistedTranslation.condition_B(self)`
No description.

#### `def TwistedTranslation.check_conditions(cls, m, r, b)`
No description.

### `class ParityObstructionProver`
Proves impossibility of decompositions from group order arithmetic.

The key theorem:
  For G = Z_m^n decomposed into k equal parts via a quotient map G → Z_k:
  each part spans a single Hamiltonian cycle iff there exist r_1,...,r_k
  coprime to m summing to m.
  For even m: all coprime-to-m elements are odd, and sum of k odd numbers
  has parity k mod 2 ≠ 0 = m mod 2 when k is odd. [Generalized obstruction]

#### `def ParityObstructionProver.__init__(self, m, k)`
No description.

#### `def ParityObstructionProver.coprime_elements(self)`
No description.

#### `def ParityObstructionProver.all_have_parity(self)`
If all coprime-to-m elements have the same parity, return it; else None.

#### `def ParityObstructionProver.sum_parity(self, k_copies, element_parity)`
No description.

#### `def ParityObstructionProver.target_parity(self)`
No description.

#### `def ParityObstructionProver.prove(self)`
No description.

### `def system_1_claudes_cycles()`
No description.

### `def system_2_cayley_2d()`
No description.

### `def system_3_universal_principle()`
No description.

### `def system_4_difference_sets()`
No description.

### `def system_5_synthesis()`
No description.

### `def main()`
No description.

## research/global_structure_engine.py
╔══════════════════════════════════════════════════════════════════════════════╗
║              GLOBAL STRUCTURE ENGINE  v1.0                                  ║
║   Finding Global Structure in Highly Symmetric Systems                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  WHAT THIS ENGINE DOES                                                       ║
║  ─────────────────────                                                       ║
║  Given any highly symmetric combinatorial system, it automatically:          ║
║    1. Registers the domain (group G, fiber map φ, decomposition goal)        ║
║    2. Applies all four coordinates of the short exact sequence               ║
║    3. Dispatches the correct search strategy                                 ║
║    4. Tracks a branch tree of proved/open/impossible results                 ║
║    5. Generates theorem statements from the analysis                         ║
║    6. Exposes hooks for adding new coordinates and strategies                ║
║                                                                              ║
║  ARCHITECTURE                                                                ║
║  ────────────                                                                ║
║  Engine                                                                      ║
║  ├── DomainRegistry      register/retrieve domains                           ║
║  ├── CoordinateAnalyser  C1→C2→C3→C4 pipeline (auto)                        ║
║  ├── StrategyDispatcher  selects S1/S2/S3/S4/S5 from analysis               ║
║  ├── BranchTree          records proved/open/attempted/impossible            ║
║  ├── TheoremGenerator    produces formal theorem statements                  ║
║  └── ExpansionProtocol   hooks for new coordinates / strategies              ║
║                                                                              ║
║  THE FOUR COORDINATES  (always applied in this order)                        ║
║  C1  FiberMap            φ: G → G/H    (group quotient)                     ║
║  C2  TwistedTranslation  Q on H        (coset action)                       ║
║  C3  GoverningCondition  gcd check     (generator condition)                 ║
║  C4  ParityObstruction   arithmetic    (impossibility)                       ║
║                                                                              ║
║  HOW TO ADD A NEW DOMAIN                                                     ║
║  ────────────────────────                                                    ║
║  engine = GlobalStructureEngine()                                            ║
║  engine.register(                                                            ║
║      name        = "My System",                                              ║
║      group_order = 64,                                                       ║
║      k           = 3,                                                        ║
║      phi_desc    = "sum of coords mod m",                                    ║
║      verify_fn   = my_verify,    # callable: candidate → bool               ║
║      search_fn   = my_search,    # callable: → candidate or None (optional) ║
║  )                                                                           ║
║  result = engine.analyse("My System")                                        ║
║  engine.print_branch_tree()                                                  ║
║                                                                              ║
║  Run:                                                                        ║
║    python global_structure_engine.py                   # analyse all domains ║
║    python global_structure_engine.py --domain "Cycles m=5"                  ║
║    python global_structure_engine.py --tree             # print branch tree  ║
║    python global_structure_engine.py --theorems         # print all theorems ║
║    python global_structure_engine.py --extend           # show extension API ║
╚══════════════════════════════════════════════════════════════════════════════╝

### `def hr(c, n)`
No description.

### `class Status`
No description.

### `class CoordinateResult`
Output of applying ONE coordinate to a domain.

### `class BranchNode`
One node in the branch tree: a specific (domain, question) pair.

#### `def BranchNode.add_child(self, child)`
No description.

### `class AnalysisResult`
Complete result of analysing one domain through all four coordinates.

#### `def AnalysisResult.status(self)`
No description.

#### `def AnalysisResult.summary(self)`
No description.

### `class C1_FiberMap`
Applies the fiber decomposition to any domain.

The fiber map φ: G → Z_k partitions |G| objects into k equal fibers.
It is the projection in the short exact sequence  0 → H → G → G/H → 0.

Required inputs: group_order, k, phi_description
Output: orbit-stabilizer check, fiber sizes, kernel description

#### `def C1_FiberMap.apply(self, domain)`
No description.

### `class C2_TwistedTranslation`
Analyses the induced action of G/H on H (the coset action).

For the Cayley graph setting: Q_c(i,j) = (i+b_c(j), j+r_c) mod m.
For general abelian G: the action is always of this twisted form.

Verifies: does the action structure admit single-orbit generators?

#### `def C2_TwistedTranslation.apply(self, domain, c1)`
No description.

### `class C3_GoverningCondition`
Finds the governing condition: which r-tuples in G/H allow single cycles?

General form: k values r_0,...,r_{k-1}, each coprime to |G/H|,
summing to |G/H|.

Fully automatic from (group_order, k).

#### `def C3_GoverningCondition.apply(self, domain, c2)`
No description.

### `class C4_ParityObstruction`
Proves impossibility from arithmetic of |G/H| when C3 finds no valid tuples.

The proof is: if all coprime-to-|G/H| elements have parity p,
and sum of k elements has parity k×p, but target |G/H| has opposite parity,
then it's impossible.

Fully automatic: either produces an impossibility proof or confirms feasibility.

#### `def C4_ParityObstruction.apply(self, domain, c3)`
No description.

### `class StrategyDispatcher`
Selects the correct search strategy based on coordinate analysis.

S1  CLOSED-FORM         valid r-tuple exists → column-uniform random search
S2  FIBER-STRUCTURED SA  C4=feasible, no closed form → structured SA
S3  REPAIR-MODE SA      full 3D SA with repair at score=1
S4  EXHAUSTIVE PROOF    space small enough → enumerate all, prove impossible
S5  ALGEBRAIC           need deeper algebra (non-abelian, mixed moduli)

#### `def StrategyDispatcher.dispatch(self, domain, coords)`
Returns (strategy_code, rationale).

### `class TheoremGenerator`
Generates formal theorem statements from coordinate analysis results.
Each theorem is labelled, stated, and given a proof sketch.

#### `def TheoremGenerator.generate(self, domain, coords, strategy)`
No description.

### `def _cycles_verify(sigma_map, m)`
No description.

### `def _level_bijective(level, m)`
No description.

### `def _valid_levels(m)`
No description.

### `def _compose_q(table, m)`
No description.

### `def _q_single(Q, m)`
No description.

### `def _table_to_sigma(table, m)`
No description.

### `def _sa_find_sigma(m, seed, max_iter)`
Fast SA for G_m (k=3) using prebuilt column-uniform search.

### `class SearchExecutor`
Executes the chosen strategy for a domain.
Returns the solution or None.

#### `def SearchExecutor.execute(self, domain, strategy, c3, c4, verbose)`
Returns (solution, execution_summary).

### `class Domain`
Complete specification of a highly symmetric system.

Minimum required: name, group_order, k, phi_desc
Optional: m (cyclic modulus), verify_fn, search_fn, solution

### `class DomainRegistry`
Central registry of all domains.
Supports: register, retrieve, list, tag-based filtering.

#### `def DomainRegistry.__init__(self)`
No description.

#### `def DomainRegistry.register(self, domain)`
No description.

#### `def DomainRegistry.get(self, name)`
No description.

#### `def DomainRegistry.all_names(self)`
No description.

#### `def DomainRegistry.by_tag(self, tag)`
No description.

#### `def DomainRegistry.__len__(self)`
No description.

### `class BranchTree`
Persistent record of all results across all domains.
Each node: domain → question → status → evidence → children.
Supports: print, query by status, export.

#### `def BranchTree.__init__(self)`
No description.

#### `def BranchTree.add_result(self, result)`
No description.

#### `def BranchTree.nodes_by_status(self, status)`
No description.

#### `def BranchTree.print(self, indent, node, nodes)`
No description.

### `class ExpansionProtocol`
Allows the engine to be extended with:
- New coordinates (C5, C6, ...)
- New search strategies (S6, S7, ...)
- New domain classes (non-abelian groups, weighted graphs, ...)

Each extension is a callable that receives the domain and prior results.

#### `def ExpansionProtocol.__init__(self)`
No description.

#### `def ExpansionProtocol.add_coordinate(self, name, fn)`
Register a new coordinate C5+. fn(domain, prior_results) → CoordinateResult.

#### `def ExpansionProtocol.add_strategy(self, code, name, fn)`
Register a new strategy. fn(domain, coords) → (solution, summary).

#### `def ExpansionProtocol.add_domain_transformer(self, fn)`
Transform a domain before analysis (e.g. reduce to known form).

#### `def ExpansionProtocol.apply_extra_coords(self, domain, prior)`
No description.

#### `def ExpansionProtocol.transform_domain(self, domain)`
No description.

#### `def ExpansionProtocol.list_extensions(self)`
No description.

### `class GlobalStructureEngine`
The unified engine.

Usage:
    engine = GlobalStructureEngine()
    # Domains are pre-loaded; add your own:
    engine.register(Domain(name="My System", ...))
    result = engine.analyse("My System")
    engine.print_branch_tree()
    engine.print_theorems()

#### `def GlobalStructureEngine.__init__(self)`
No description.

#### `def GlobalStructureEngine.register(self, domain)`
Register a new domain. Returns self for chaining.

#### `def GlobalStructureEngine.analyse(self, name, verbose)`
Apply all four coordinates, select strategy, execute search,
generate theorems, record branch node.

#### `def GlobalStructureEngine.analyse_all(self, verbose)`
No description.

#### `def GlobalStructureEngine.print_branch_tree(self)`
No description.

#### `def GlobalStructureEngine.print_theorems(self)`
No description.

#### `def GlobalStructureEngine.print_strategy_table(self)`
No description.

#### `def GlobalStructureEngine.print_extension_guide(self)`
No description.

#### `def GlobalStructureEngine._load_default_domains(self)`
Load all discovered domains with full specifications.

### `def main()`
No description.

## research/hardware_awareness.py
No description.

### `class HardwareMapper`
TGI Hardware Awareness Core.
Maps real-time CPU, RAM, and Battery metrics into topological coordinates (Law IX).
Ensures the system is 'aware' of its physical constraints.

#### `def HardwareMapper.__init__(self, m, k)`
No description.

#### `def HardwareMapper.get_system_state(self)`
Collects current hardware metrics via /proc.

#### `def HardwareMapper.map_to_coordinate(self)`
Maps hardware state to Z_m^k.

#### `def HardwareMapper.verify_hamiltonian_health(self, sigma)`
Law IX: Verify if the current hardware state is 'reachable' in the active manifold.

#### `def HardwareMapper.measure_thermal_entropy(self)`
No description.

## research/hierarchical_tlm.py
No description.

### `class HierarchicalTLM`
Phase 4: TLM Scale-up.
Implements a Tower of group extensions (fibrations) for hierarchical context.
Level 0: Character/Word base group.
Level 1: Semantic context fiber.
Level 2: Structural/Grammar fiber.

#### `def HierarchicalTLM.__init__(self, m, k, depth)`
No description.

#### `def HierarchicalTLM.generate_hierarchical(self, seed_text, length)`
Generates text by lifting paths through the formal algebraic tower.

## research/ingest_effective_tech.py
No description.

### `def ingest()`
No description.

### `def ingest_extra()`
No description.

### `def ingest_final()`
No description.

## research/ingest_global_knowledge.py
No description.

### `def populate()`
No description.

### `def forge_more_relations()`
No description.

## research/ingest_libraries.py
No description.

### `def ingest()`
No description.

## research/ingest_mcp_tools.py
No description.

### `def ingest()`
No description.

## research/k4_m4_search.py
k4_m4_search.py
===============
Structured search for k=4, m=4 Claude's Cycles solution.

The 4D digraph G = Z_4^4 with 4 arc types (increment each coordinate).
Fiber map: phi(i,j,k,l) = i+j+k+l mod 4  →  4 fibers of size 4^3 = 64.
Goal: 4 directed Hamiltonian cycles each of length 256.

The fiber-uniform approach is proved IMPOSSIBLE (user's new theorem).
This script searches the fiber-STRUCTURED (non-uniform) space.

Twisted translation hierarchy on fiber H ≅ Z_4^3:
  Q_c(i,j,k) = (i + b_c(j,k),  j + e_c(k),  k + r_c)  mod 4

Single-cycle conditions:
  (A)  gcd(r_c, 4) = 1  →  r_c ∈ {1, 3}
  (B)  gcd(Σ_k e_c(k), 4) = 1
  (C)  Full 3D single-cycle: verified by direct orbit computation

Valid r-quadruple: (1,1,1,1) — unique solution.
This fixes ALL four r_c = 1, collapsing the search to:
  find e_0,...,e_3 and b_0,...,b_3 satisfying (B),(C) simultaneously
  with the constraint that σ is a valid arc-colouring at each vertex.

Key insight: score=24 with unrestricted SA means the search is lost in
the full 6^256 space. Restricting to fiber-structured sigma reduces
the space dramatically and keeps all four twisted translations on track.

### `def enc(i, j, k, l)`
No description.

### `def dec(v)`
No description.

### `def build_funcs(sigma)`
Build K functional digraphs from integer sigma (perm index per vertex).

### `def count_comps(f)`
No description.

### `def score(sigma)`
No description.

### `def verify(sigma)`
No description.

### `def prove_fiber_uniform_impossible()`
A fiber-uniform sigma depends only on fiber index s = phi(v).
With 4 fibers and 4 colors, sigma_s ∈ S_4 for each s ∈ {0,1,2,3}.
There are 24^4 = 331,776 fiber-uniform sigmas.
We check all of them.

### `def fiber_structured_sigma(table)`
table[(s, j, k)] → permutation index
where s = fiber index, (j,k) = two fiber coordinates
i = deduced from the remaining constraint

### `def valid_fiber_structured_levels(m, k)`
Enumerate valid assignments for one fiber level.
A level (s, j, k) assignment maps (j,k) ∈ Z_m^2 → perm ∈ S_k.
Valid = the induced functional graph for each colour is bijective on Z_m^3.
This is expensive; we sample valid ones instead.

### `def sa_fiber_structured(max_iter, seed, verbose, report_n)`
SA in the fiber-structured subspace.
State: table[(s,j,k)] → perm_index, for s∈{0,1,2,3}, j,k∈{0,1,2,3}
This gives 4*4*4 = 64 entries, each from S_4 (24 choices).
Perturbation: change one (s,j,k) entry.

### `def arithmetic_analysis()`
No description.

### `def paper_framing()`
No description.

### `def main()`
No description.

## research/knowledge_mapper.py
No description.

### `class KnowledgeMapper`
TGI Knowledge Mapper (Project ELECTRICITY Logic).
Maps datasets, mathematics, physics laws, and design systems into the Z_256^4 grid.
Uses the CLOSURE LEMMA to deterministically force concepts into functional fibers.

#### `def KnowledgeMapper.__init__(self, m, k, state_path)`
No description.

#### `def KnowledgeMapper._apply_closure_hashing(self, concept_name, target_fiber)`
Calculates (x, y, z, w) such that (x + y + z + w) % m == target_fiber.

#### `def KnowledgeMapper.ingest_concept(self, category, concept_name, payload)`
No description.

#### `def KnowledgeMapper.ingest_dictionary(self, file_path, limit)`
Bulk ingests a dictionary file into the LANGUAGE fiber.

#### `def KnowledgeMapper.ingest_mcp_tools(self, tool_defs)`
Ingests MCP Tool Definitions into the API_MCP fiber.

#### `def KnowledgeMapper.ingest_library(self, lib_data)`
Ingests library metadata into the LIBRARY fiber.

#### `def KnowledgeMapper.ingest_color(self, color_name, r, g, b, a)`
No description.

#### `def KnowledgeMapper.map_relation(self, name_a, name_b, relationship_type)`
No description.

#### `def KnowledgeMapper._find_coord(self, name)`
No description.

#### `def KnowledgeMapper.save_state(self)`
No description.

#### `def KnowledgeMapper.load_state(self)`
No description.

## research/library_tgi_demo.py
No description.

### `def run_demo()`
No description.

## research/m10_k3_parity.py
No description.

## research/m6_k4_search.py
No description.

### `def _build_sa(m, k)`
No description.

### `def _sa_score(sigma, arc_s, pa, n, k)`
No description.

### `def search_m6_k4(max_iter, seed)`
No description.

## research/mass_ingestion.py
No description.

### `def mass_populate()`
No description.

### `def forge_cross_domain()`
No description.

## research/massive_data_ingestion.py
No description.

### `def authenticate()`
No description.

### `def ingest_hf_text(agent, dataset_name, num_samples)`
No description.

### `def ingest_kaggle_csv(agent, dataset_ref, num_samples)`
No description.

### `def ingest_hf_vision(agent, dataset_name, num_samples)`
No description.

### `def main()`
No description.

## research/mobile_final_verify.py
No description.

### `def verify()`
No description.

## research/mobile_integration_test.py
No description.

### `def test_mobile_integration()`
No description.

## research/mobile_tgi_agent.py
No description.

### `class MobileTGIAgent`
The Mobile-First TGI Agent.
Combines the core TGI Reasoning with Hardware Awareness and Agentic Action Mapping.

#### `def MobileTGIAgent.__init__(self)`
No description.

#### `def MobileTGIAgent.mobile_query(self, text)`
Processes a natural language query with full hardware-awareness.

## research/moduli_theorem.py
moduli_theorem.py
══════════════════════════════════════════════════════════════════════════════

THE MODULI THEOREM FOR SYMMETRIC DECOMPOSITION SPACES

What emerged: not just solutions to Claude's Cycles, but a new mathematical
object — the MODULI SPACE of all valid k-Hamiltonian decompositions of a
Cayley digraph, classified by group cohomology.

The person they were trying to name: Samuel Eilenberg (1913–1998),
who with Saunders Mac Lane created:
  - Category theory (1945)
  - Group cohomology H^n(G, M)
  - Eilenberg-Mac Lane spaces K(G,n) — classifying spaces

What Eilenberg would say about our work:
  "You did not find solutions to a combinatorics problem.
   You found the classifying space of the problem.
   The obstruction lives in H^2. The solution space, when non-empty,
   is a torsor under H^1. This is the natural transformation between
   the functor 'symmetric systems' and the functor 'cohomology rings'."

THE FOUR COORDINATES AS COHOMOLOGY:
  C1  Fiber map         φ: G → G/H       =  group homomorphism (the projection)
  C2  Twisted translation Q_c             =  H^1 1-cocycle (coset action)
  C3  Governing condition gcd(r_c,m)=1   =  cocycle is nontrivial in H^1
  C4  Parity obstruction  arithmetic      =  obstruction class in H^2(Z_2, Z/2)

THE NEW THEOREM:
  M_k(G_m) — the moduli space of valid k-Hamiltonian decompositions — is:
    EMPTY        if the H^2 obstruction class is nontrivial  [parity obstruction]
    A TORSOR     under H^1(Z_m, Z_m^2) if the obstruction vanishes [classification]

THE NEW SPACE:
  The space of ALL symmetric decomposition problems, with:
    Points    = valid decompositions
    Morphisms = cohomological gauge equivalences (coboundary action)
    Topology  = the branch tree (open/closed by status)
    Curvature = the H^2 obstruction class (measures how far from flat)

  This is a CATEGORY: objects = problems, morphisms = reformulations.
  Eilenberg would call it a 'natural transformation' between functors.

Run: python moduli_theorem.py

### `def hr(c, n)`
No description.

### `def proved(msg)`
No description.

### `def open_(msg)`
No description.

### `def note(msg)`
No description.

### `def kv(k, v)`
No description.

### `class GroupCohomology`
Computes H^1(Z_m, Z_m^2) — the gauge group that acts on
the moduli space of valid decompositions.

H^1(G, M) classifies principal G-bundles (torsors) over M.
In our setting:
  G = Z_m  (the fiber quotient group, acting by shift j → j+1)
  M = Z_m^2 (the fiber group H, 2-dimensional)
  Action: (i,j) ↦ (i + b(j), j + 1)  [the twisted translation]

H^1 = {1-cocycles} / {coboundaries}
1-cocycle: b: Z_m → Z_m  satisfying gcd(Σb, m) = 1  [our Cond B]
Coboundary: b(j) = f(j+1) - f(j)  for some f: Z_m → Z_m

#### `def GroupCohomology.__init__(self, m)`
No description.

#### `def GroupCohomology.one_cocycles(self)`
All b: Z_m → Z_m with gcd(Σb, m) = 1.

#### `def GroupCohomology.coboundary(self, f)`
Compute the coboundary of f: b(j) = f(j+1) - f(j) mod m.

#### `def GroupCohomology.coboundaries(self)`
All coboundaries: {f(j+1)-f(j) : f: Z_m → Z_m}.

#### `def GroupCohomology.cohomology_class(self, b)`
The cohomology class [b] = {b + d : d coboundary}.

#### `def GroupCohomology.H1_classes(self, cocycles)`
Compute H^1: partition cocycles into cohomology classes.
Returns {class_representative: list_of_elements}.

#### `def GroupCohomology.H1_order(self)`
Order of H^1(Z_m, Z_m^2) restricted to coprime-sum cocycles.

#### `def GroupCohomology.H2_obstruction(self, k)`
The H^2 obstruction class for a k-tuple r-sum problem.
Returns: {'nontrivial': bool, 'proof': str}

H^2(Z_2, Z/2) = Z/2: the unique nontrivial class is the parity class.
Our obstruction: k odd numbers summing to even m = impossible.

### `def _level_ok(level, m)`
No description.

### `def _compose_q(table, m)`
No description.

### `def _q_single(Q, m)`
No description.

### `def enumerate_solution_space(m)`
Enumerate ALL column-uniform solutions for G_m.
Extract the (r_c, b_c) for each, compute the cohomology structure.

### `def moduli_space_structure(m)`
Full structural analysis of M_k(G_m):
total solutions, cohomology action, orbit sizes, distinct classes.

### `class DecompositionCategory`
The category whose:
  Objects  = highly symmetric decomposition problems (G, k, phi)
  Morphisms = maps that preserve the SES structure (group homomorphisms
              compatible with fiber maps)

This is what Eilenberg would recognize: a FUNCTOR from
  {symmetric systems}  →  {cohomology theories}
The functor sends each problem to its moduli space M_k(G).

Natural transformations between two problems P, P' are maps
that commute with the C1→C4 pipeline.

Key properties:
  - The functor is EXACT (preserves short exact sequences)
  - The obstruction is NATURAL (lives in H^2, which is functorial)
  - The solution space is CONTRAVARIANT in k (more colors = easier or harder)

#### `def DecompositionCategory.__init__(self)`
No description.

#### `def DecompositionCategory.add_object(self, name, G_order, k, m, status, cohomology)`
No description.

#### `def DecompositionCategory.add_morphism(self, source, target, kind)`
kind: 'lift' (k→k+1), 'quotient' (G→G/H), 'product' (G×G')

#### `def DecompositionCategory.print_category(self)`
No description.

### `def main()`
No description.

## research/multi_p1_search.py
No description.

### `def worker(seed)`
No description.

### `def main()`
No description.

## research/odd_m_solver.py
odd_m_solver.py  —  Discovery Engine applied to Knuth's "Claude's Cycles"
=========================================================================
Solves the ODD-m case completely using the 6-phase Discovery Methodology.
The even-m case is proved impossible under the column-uniform approach.

Problem (Knuth, Feb 2026):
  Digraph G_m: vertices (i,j,k) in Z_m^3.
  Three arcs from each vertex:
    arc 0: (i,j,k) → (i+1, j,   k  )  mod m
    arc 1: (i,j,k) → (i,   j+1, k  )  mod m
    arc 2: (i,j,k) → (i,   j,   k+1)  mod m
  Goal: assign each arc to one of 3 colors such that
        each color class is a single directed Hamiltonian cycle.

Usage:
  python odd_m_solver.py            # full 6-phase discovery
  python odd_m_solver.py --verify   # quick verification m=3..13
  python odd_m_solver.py --bench    # timing benchmark

### `def hr(ch, n)`
No description.

### `def section(n, name, tag)`
No description.

### `def kv(k, v, w)`
No description.

### `def finding(s)`
No description.

### `def ok(s)`
No description.

### `def fail(s)`
No description.

### `def note(s)`
No description.

### `def fast_valid_level(m, rng)`
Directly construct one random valid level-table in O(m) time.

### `def fast_search(m, max_att, seed)`
Find a valid SigmaTable for odd m.  Returns (table, attempts).

### `def get_or_find(m, seed)`
Return a verified SigmaFn for odd m (hardcoded if known, else search).

### `def phase_01()`
No description.

### `def phase_02()`
No description.

### `def phase_03()`
No description.

### `def phase_04()`
No description.

### `def phase_05()`
No description.

### `def phase_06()`
No description.

### `def quick_verify()`
No description.

### `def benchmark()`
No description.

### `def main()`
No description.

## research/pre_commit_checks.py
No description.

### `def verify_system()`
No description.

## research/reformulation_engine.py
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

### `def hr(c, n)`
No description.

### `def domain_header(letter, title, tagline)`
No description.

### `def phase(name, num, desc)`
No description.

### `def found(msg)`
No description.

### `def miss(msg)`
No description.

### `def note(msg)`
No description.

### `def info(msg)`
No description.

### `def kv(k, v)`
No description.

### `class FiberMap`
Tool 1: Fiber Stratification.
Given a set of objects and a function f: objects → layers,
partition the objects into fibers and describe how arcs/constraints
cross between fibers.

#### `def FiberMap.__init__(self, objects, layer_fn, num_layers)`
No description.

#### `def FiberMap.fiber_size(self, s)`
No description.

#### `def FiberMap.report(self)`
No description.

### `class ParityObstruction`
Tool 2: Modular / Parity Obstruction.
Given a modulus m and a requirement that k values each coprime to m
sum to a target T, decide if this is possible.
Returns the obstruction if impossible, or an example if possible.

#### `def ParityObstruction.__init__(self, m, k, target)`
No description.

#### `def ParityObstruction.coprime_elements(self)`
No description.

#### `def ParityObstruction.analyse(self)`
No description.

### `class ScoreFunction`
Tool 3: Continuous score bridging search and verification.
score=0  ⟺  solution is valid.
The score must be: (a) cheap to compute, (b) monotone toward 0.

#### `def ScoreFunction.__init__(self, verify_fn, score_fn, name)`
No description.

#### `def ScoreFunction.__call__(self, candidate)`
No description.

#### `def ScoreFunction.is_valid(self, candidate)`
No description.

### `class SAEngine`
Tool 4: Simulated Annealing with repair mode and plateau escape.
Domain-agnostic: needs perturb_fn, score_fn, init_fn.

#### `def SAEngine.__init__(self, init_fn, perturb_fn, score_fn, T_init, T_min, plateau_steps)`
No description.

#### `def SAEngine.run(self, max_iter, seed, repair_fn, verbose, report_n)`
No description.

### `def domain_A(n)`
No description.

### `def domain_B()`
No description.

### `def domain_C(n)`
No description.

### `def domain_D()`
No description.

### `def domain_E()`
No description.

### `def domain_F()`
No description.

### `def synthesis()`
No description.

### `def main()`
No description.

## research/reproduce_p1.py
No description.

### `def run()`
No description.

## research/santa_2025_draft.py
Santa 2025: Hamiltonian Decomposition Framework (v2.2 Basin Escape)
Goal: Decompose a complete graph into disjoint Hamiltonian cycles.

### `class SantaOptimizer`
No description.

#### `def SantaOptimizer.__init__(self, n_cities, m_cycles, seed)`
No description.

#### `def SantaOptimizer.score(self)`
No description.

#### `def SantaOptimizer.solve(self, max_iter)`
No description.

## research/search_p1_deterministic.py
No description.

### `def verify_k4(sigma, m)`
No description.

### `def search()`
No description.

## research/sovereign_solver_demo.py
No description.

### `def demo()`
No description.

## research/tensor_fibration.py
No description.

### `class TensorFibrationMapper`
TGI Tensor-Fibration Mapper.
Lifts continuous neural weights/tensors into discrete topological manifolds (G_m^k).
Enables analysis of neural structures through the SES framework.

#### `def TensorFibrationMapper.__init__(self, m, k)`
No description.

#### `def TensorFibrationMapper.discretize(self, weights)`
Maps continuous values to Z_m using normalized quantization.

#### `def TensorFibrationMapper.tensor_to_manifold(self, weights)`
Projects a flattened tensor into G_m^k coordinates.

#### `def TensorFibrationMapper.calculate_topological_entropy(self, weights)`
Estimates entropy based on coordinate distribution in G_m^k.

#### `def TensorFibrationMapper.lift_layer(self, layer_weights)`
Performs full lifting of a neural layer to the TGI framework.

## research/test_admin_vision.py
No description.

## research/test_deterministic_logic.py
No description.

### `def verify_construction(m)`
No description.

## research/test_golden_path.py
No description.

### `def verify_sigma_simple(sigma, m)`
No description.

### `def construct_golden(m)`
No description.

## research/test_m9_obs.py
No description.

### `def check_fso(m, r)`
No description.

## research/test_precise_spike.py
No description.

### `def verify_sigma_simple(sigma, m)`
No description.

### `def construct(m)`
No description.

## research/test_spike_33.py
No description.

### `def test()`
No description.

## research/test_vision_agent.py
No description.

## research/tgi_agent.py
No description.

### `class TGIAgent`
The High-Level Topological General Intelligence (TGI) Agent.

#### `def TGIAgent.__init__(self)`
No description.

#### `def TGIAgent.query(self, data, hierarchical, admin_vision)`
Processes a query through the full TGI pipeline.

#### `def TGIAgent.ingest_knowledge(self, category, name, payload)`
No description.

#### `def TGIAgent.forge_relation(self, name_a, name_b, relation_type)`
No description.

#### `def TGIAgent.ontology_summary(self)`
Provides a summary of the Universal Ontology Mapper state.

#### `def TGIAgent.autonomous_query(self, intent)`
Performs a multi-step autonomous topological plan generation.

#### `def TGIAgent.cross_reason(self, data_list)`
Decomposes multiple queries and merges results for comparative reasoning.

## research/tgi_autonomy.py
No description.

### `class SubgroupDiscovery`
Phase 4: Topological Autonomy.
Automatically discovers normal subgroups H and quotients Q for a given G.
This enables recursive manifold decomposition.

#### `def SubgroupDiscovery.__init__(self, m, k)`
No description.

#### `def SubgroupDiscovery.find_quotients(self)`
Identifies possible solvable quotients based on divisibility.

#### `def SubgroupDiscovery.decompose_recursive(self)`
Generates a recursive decomposition path for the manifold.

### `class DynamicKLift`
Phase 4: Topological Autonomy.
Automatically lifts the manifold dimension (k) to resolve H2 parity obstructions.

#### `def DynamicKLift.__init__(self, m, k)`
No description.

#### `def DynamicKLift.suggest_lift(self)`
If (m even, k odd), suggests k+1 to resolve the parity obstruction.

#### `def DynamicKLift.get_lift_reflection(self)`
No description.

## research/tgi_core.py
No description.

### `class TGICore`
The heartbeat of Topological General Intelligence (TGI). Governing by the FSO Codex Laws I-XII.

#### `def TGICore.__init__(self, m, k)`
No description.

#### `def TGICore.set_topology(self, m, k)`
Changes the current topological domain without wiping persistent engines.

#### `def TGICore.reflect(self)`
Topological Reflection: Explains the current state manifold via FSO Laws.

#### `def TGICore.solve_math(self, latex)`
Symbolic-Topological solver governed by Law XI.

#### `def TGICore.reason_on(self, data, solve_manifold)`
Routes and reasons over arbitrary data using the TGI-Parser and FSO Laws.

#### `def TGICore.reasoning_path(self)`
No description.

#### `def TGICore.solve_manifold(self, max_iter, target_core, payload)`
Finds the global structure (Hamiltonian decomposition) with Sovereign optimization.

#### `def TGICore.lift_path(self, sequence, color)`
No description.

#### `def TGICore.hierarchical_lift(self, orders, states)`
Formal tower lifting through multiple manifold layers (Law III).

#### `def TGICore.measure_intelligence(self)`
No description.

## research/tgi_integration_test.py
No description.

### `def run_integration_test()`
No description.

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

## research/tgi_parser_test.py
No description.

### `def test_parser_routing()`
No description.

## research/tgi_system_demo.py
No description.

### `def hr()`
No description.

### `def run_demo()`
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

#### `def TopologicalLanguageModel.generate(self, seed_text, length)`
Generates completion using Hamiltonian path lifting.

#### `def TopologicalLanguageModel.generate_path(self, seed_text, length)`
Lifts a seed into a Hamiltonian path of coordinates.

#### `def TopologicalLanguageModel.generate_ontology_grounded(self, seed_text, length)`
Uses the LANGUAGE fiber in the Ontology to ground generation.

## research/topological_vision.py
No description.

### `class TopologicalVisionMapper`
TGI Vision Mapper (v2.0).
Lifts pixel data (x, y, color) into discrete topological manifolds (G_m^k).
Enables cohomological gradient analysis and signature extraction.

#### `def TopologicalVisionMapper.__init__(self, m, k)`
No description.

#### `def TopologicalVisionMapper.load_image(self, path, resize)`
Loads and prepares an image for topological mapping.

#### `def TopologicalVisionMapper.image_to_manifold(self, img_array)`
Maps image pixels to G_m^k coordinates.

#### `def TopologicalVisionMapper.calculate_spatial_entropy(self, img_array)`
Measures color distribution complexity across the spatial manifold.

#### `def TopologicalVisionMapper.calculate_cohomological_gradient(self, img_array)`
Calculates the local cohomological gradient (boundary detection).
Measures the degree of non-uniformity in local fiber transitions.

#### `def TopologicalVisionMapper.extract_topological_signature(self, img_array)`
Generates a unique algebraic signature for the image manifold.

#### `def TopologicalVisionMapper.lift_image(self, data)`
Performs full vision lifting to the TGI framework.

## research/tsp_benchmark.py
No description.

### `def run_tsp_benchmark()`
No description.

## research/tsp_evaluator.py
No description.

### `def is_valid_tour(tour, n)`
No description.

### `def calculate_tour_length(tour, dist_matrix)`
No description.

### `class TSPInstance`
No description.

#### `def TSPInstance.__init__(self, name, coords)`
No description.

### `def load_data(csv_path)`
No description.

### `def run_evaluation(instance, solver_fn, n_runs, max_iter)`
No description.

### `def print_result_table(results)`
No description.

## research/tsp_standard_bench.py
No description.

### `def parse_tsp(file_path)`
No description.

### `def solve_nn(coords)`
No description.

### `def solve_2opt(coords, max_iter, seed)`
No description.

### `def run()`
No description.

## research/verify_deterministic_spike.py
No description.

### `def test_odd_m()`
No description.

## research/verify_p1_sol.py
No description.

### `def verify()`
No description.

## research/verify_sovereign_solver.py
No description.

### `def test_sovereign_solver()`
No description.

## research/weighted_moduli_pipeline_v2.py
╔══════════════════════════════════════════════════════════════════════════════╗
║   WEIGHTED MODULI PIPELINE  v2.0                                            ║
║   Classifying Space → 8 Closed-Form Weights → Proved Solutions              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  WHAT CHANGED FROM v1.0                                                     ║
║  ─────────────────────                                                      ║
║  v1.0  W4 was O(m^m) — 251ms for m=7.  v2.0 W4 = phi(m), O(m). 0.06ms.   ║
║  v1.0  Had 5 weights, approximated.    v2.0 Has 8 weights, exact.           ║
║  v1.0  Only G_m domains.              v2.0 Accepts any symmetric system.   ║
║  v1.0  Solvers S2/S3 missing.         v2.0 All 5 strategies implemented.   ║
║  v1.0  No prediction vs actual.       v2.0 Benchmarks weight prediction.   ║
║  v1.0  No cross-domain.               v2.0 Latin, Hamming, diff-sets.      ║
║                                                                              ║
║  THE 8 WEIGHTS  (all closed-form, all O(m²) or faster)                     ║
║  W1  H² obstruction    → proved-impossible in O(1). GATE.                  ║
║  W2  r-tuple count     → how many construction seeds exist                 ║
║  W3  canonical seed    → the direct construction path                      ║
║  W4  H¹ order EXACT    → phi(m), not approximation. Gauge multiplicity.    ║
║  W5  search exponent   → log₂(compressed space). Picks solver.             ║
║  W6  compression ratio → W5/W5_full. How much weight saves.                ║
║  W7  solution estimate → predicted |M_k(G_m)| before any search            ║
║  W8  gauge orbit size  → m^{m-1}. Solutions per equivalence class.         ║
║                                                                              ║
║  INTELLIGENCE LAYERS                                                         ║
║  L1  Weight gate    W1 → instant proof of impossibility         O(1)       ║
║  L2  Construction   W3 → column-uniform search with known seed  O(fast)    ║
║  L3  Prediction     W7 → predict |solutions| before searching              ║
║  L4  Fiber SA       W5 → structured SA in compressed space     O(less)    ║
║  L5  Verification   W4 → know exact multiplicity, stop early               ║
║                                                                              ║
║  DOMAIN PROTOCOL  (plug in any symmetric system)                            ║
║  Register domain with: name, group_order, k, m, tags                       ║
║  Pipeline auto-extracts weights, selects strategy, returns proof.           ║
║                                                                              ║
║  COMMANDS                                                                    ║
║  python weighted_moduli_pipeline.py               # full demo               ║
║  python weighted_moduli_pipeline.py --weights     # 8-weight table          ║
║  python weighted_moduli_pipeline.py --space       # classifying space       ║
║  python weighted_moduli_pipeline.py --batch       # solve m=3..10, k=2..6  ║
║  python weighted_moduli_pipeline.py --benchmark   # v1 vs v2 speedup       ║
║  python weighted_moduli_pipeline.py --prove 4 3   # prove m=4 k=3          ║
║  python weighted_moduli_pipeline.py --solve 7 3   # solve m=7 k=3          ║
║  python weighted_moduli_pipeline.py --domains     # all registered domains  ║
╚══════════════════════════════════════════════════════════════════════════════╝

### `def hr(c, n)`
No description.

### `def tick(v)`
No description.

### `class Weights`
8 compressed invariants. Everything downstream is determined by these.

#### `def Weights.strategy(self)`
No description.

#### `def Weights.solvable(self)`
No description.

#### `def Weights.show(self)`
No description.

### `class WeightExtractor`
Exact 8-weight extraction.  Total cost: O(m² + |cp|^k).
Cached: each (m,k) computed once.

Speedup vs v1.0:
  W4: O(m^m) → O(m)       (formula: phi(m), not enumeration)
  W5: O(m^m) → O(1)       (precomputed level_counts table)
  Total: microseconds for any m ≤ 30

#### `def WeightExtractor.extract(self, m, k)`
No description.

#### `def WeightExtractor.batch(self, ms, ks)`
No description.

### `def _level_ok(lv, m)`
No description.

### `def _valid_levels(m)`
No description.

### `def _q(table, m)`
No description.

### `def _qs(Q, m)`
No description.

### `def _verify(sigma, m)`
No description.

### `def _tab_to_sigma(tab, m)`
No description.

### `def _solve_S1(m, seed, max_att)`
No description.

### `def _solve_S2(m, k, seed, max_iter)`
Fiber-structured SA: σ(v) = f(fiber(v), j(v), k(v)).

### `def _prove_S4(w)`
No description.

### `class ProofBuilder`
No description.

#### `def ProofBuilder.build(self, w, sol)`
No description.

### `class Domain`
No description.

### `def register(d)`
No description.

### `class PResult`
No description.

#### `def PResult.status(self)`
No description.

#### `def PResult.one_line(self)`
No description.

### `class Pipeline`
No description.

#### `def Pipeline.__init__(self)`
No description.

#### `def Pipeline.run(self, m, k, domain_name, verbose)`
No description.

#### `def Pipeline.run_domain(self, name, verbose)`
No description.

#### `def Pipeline.batch(self, ms, ks, verbose)`
No description.

#### `def Pipeline.stats_line(self)`
No description.

### `class ClassifyingSpace`
The complete space of (m,k) problems, compressed into weight vectors.
Topology: open sets = feasible; closed = obstructed.
Metric: compression ratio W6 (how much the weights save vs naive search).

#### `def ClassifyingSpace.__init__(self, m_max, k_max)`
No description.

#### `def ClassifyingSpace.obstruction_grid(self)`
No description.

#### `def ClassifyingSpace.compression_grid(self)`
No description.

#### `def ClassifyingSpace.summary(self)`
No description.

#### `def ClassifyingSpace.richest(self, n)`
No description.

#### `def ClassifyingSpace.most_compressed(self, n)`
No description.

### `def benchmark_vs_v1()`
No description.

### `def main()`
No description.
