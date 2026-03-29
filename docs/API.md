# API Documentation

## core.py
The core engine for solving Cayley graph decompositions.

### `def extract_weights(m: int, k: int) -> Weights`
Calculates the 8 weights (W1-W8) that classify the (m, k) problem instance.

### `def solve(m, k, seed=42, max_iter=100) -> Optional[Dict]`
Unified solver that routes between precomputed solutions, deterministic construction (odd m), and hybrid simulated annealing.

### `def repair_manifold(m, k, sigma_in, max_iter=100_000) -> Optional[Dict]`
**New in Phase 4.** Last-mile optimization engine. Uses targeted Basin Escape to resolve minor Hamiltonian inconsistencies in near-solved manifolds.

## research/tgi_core.py

### `class TGICore`
The heartbeat of TGI. Manages domain state and cross-core reasoning.

#### `def reason_on(self, data, solve_manifold=True)`
**Updated in Phase 4.** Routes data via the TGI-Parser. Includes **Autonomous K-Expansion**: if a manifold is proved impossible (parity obstruction), it automatically triggers a $k$-lift to a solvable higher-dimensional space.

## research/tgi_agent.py

### `class TGIAgent`
High-level interface for TGI operations.

#### `def query(self, data, hierarchical=False)`
Processes a query through the full pipeline. Reports topological transitions and autonomous corrections (lifts).

## research/hierarchical_tlm.py

### `class HierarchicalTLM`
**New in Phase 4.** Rigorous linguistic scale-up engine.
Uses the algebraic `Tower` to navigate total manifold spaces ($G_{total}$) and projects states down to base tokens ($G_m$) for output, ensuring multi-level semantic consistency.

## research/tgi_autonomy.py

### `class DynamicKLift`
Handles the logic for manifold expansion when obstructions are detected.

### `class SubgroupDiscovery`
Automatically identifies solvable quotients and normal subgroups for recursive decomposition.

## research/topological_vision.py

### `class TopologicalVisionMapper`
**New in Phase 5.** Lifts pixel data (x, y, R, G, B) into discrete topological manifolds.
- `lift_image(data)`: Projects image array or file into $G_m^k$, returning topological entropy and point distribution.
- `calculate_spatial_entropy(img_array)`: Measures color distribution complexity across the spatial manifold.
