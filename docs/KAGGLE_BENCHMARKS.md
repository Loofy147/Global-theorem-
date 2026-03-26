# Kaggle Search Benchmarks

Results of high-budget combinatorial searches on Kaggle (March 2026).

## Problems
- **P1**: k=4, m=4 (256 vertices) - **SOLVED**
- **P2**: m=6, k=3 (216 vertices)
- **P3**: m=8, k=3 (512 vertices)

## Comparison: Standard SA vs. Equivariant SA

| Problem | Method | Iterations | Best Score | Status |
|---|---|---|---|---|
| P1 | Fiber SA (Basin-escape v3.1) | 47.8M | 0 | **Solved** |
| P2 | Standard (Basin-escape v3.0) | 20M | 4 | Open |
| P3 | Standard (Basin-escape v3.0) | 10M | 15 | Open |

### Analysis
1. **P1 Breakthrough**: The k=4, m=4 problem was solved using Fiber-Structured SA with the Basin Escape v3.1 engine. This confirms that the k=4 even-m parity resolution is indeed feasible.
2. **Convergence**: Equivariant moves (flipping entire orbits) reach local minima much faster (score=9 achieved in <1M iters) but currently plateau there.
3. **P2/P3 Barriers**: The score=4 and score=15 plateaus represent deep local minima where the basin-escape logic successfully breaks large symmetric blocks but struggles with the final few components.

## Remote Execution
Searches are offloaded to Kaggle using `kaggle_search.py` and monitored via:
```bash
python engine.py --remote
```
