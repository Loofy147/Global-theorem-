# Kaggle Search Benchmarks

Results of high-budget combinatorial searches on Kaggle GPUs (March 2026).

## Problems
- **P1**: k=4, m=4 (256 vertices)
- **P2**: m=6, k=3 (216 vertices)

## Comparison: Standard SA vs. Equivariant SA

| Problem | Method | Iterations | Best Score | Status |
|---|---|---|---|---|
| P1 | Standard (Basin-escape) | 10M | 4 | Open |
| P1 | Equivariant (Orbit-flips) | 10M | 9 | Open |
| P2 | Standard (Basin-escape) | 20M | 4 | Open |
| P2 | Equivariant (Orbit-flips) | 10M | 9 | Open |

### Analysis
1. **Convergence**: Equivariant moves (flipping entire orbits) reach local minima much faster (score=9 achieved in <1M iters) but currently plateau there.
2. **Standard SA**: The basin-escape v2.1 mechanism is highly effective at chipping away final components, reaching a score of 4 for both P1 and P2 in extended runs.
3. **P2 Barrier**: The score=9 plateau is related to the $Z_3$ symmetry (8 components of size 27). Both methods hit this, but standard SA with adaptive kicks successfully breaks it.

## Remote Execution
Searches are offloaded to Kaggle using `kaggle_search.py` and monitored via:
```bash
python engine.py --remote
```
