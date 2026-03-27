# Kaggle Search Benchmarks

Results of high-budget combinatorial searches on Kaggle (March 2026).

## Decompositions of $\mathbb{Z}_m^k$

| Problem | Method | Iterations | Best Score | Status |
|---|---|---|---|---|
| **P1** (k=4, m=4) | Fiber SA (Basin v3.1) | 47.8M | 0 | **Solved** |
| **P2** (m=6, k=3) | Frontier SA (Basin v3.3) | 20M | 4 | Open |
| **P3** (m=8, k=3) | Frontier SA (Basin v3.3) | 10M | 15 | Open |

## Traveling Salesman Problem (TSP) Standard Evaluation

| Instance | Cities | Rand Best | NN | Basin Escape | Best Known | Gap % | Time | Runs |
|---|---|---|---|---|---|---|---|---|
| bayg29 | 29 | 2078.7 | 588.1 | 588.08 | 2020 (scaled) | ~0% | 0.2s | 10 |
| att532 | 29 | 1340.7 | 616.8 | 546.72 | N/A | -11.3% (vs NN) | 0.5s | 10 |
| eil51 | 51 | 1413.1 | 449.3 | 449.32 | 426 | 5.4% | 0.5s | 5 |

*Note: The Basin Escape engine uses 2-opt swaps with simulated annealing. Gap % is calculated relative to the best known optimal value.*

## Non-Abelian & Advanced Domains

| Domain | Group | Order | k | Status | Record Score |
|---|---|---|---|---|---|
| Heisenberg | (\mathbb{Z}_3)$ | 27 | 3 | Open | 3 |
| Heisenberg | (\mathbb{Z}_6)$ | 216 | 3 | **Impossible** | H² blocks |
| 2I (Icosahedral) | (2,5)$ | 120 | 3 | **Impossible** | H² blocks |
| Hamming | $\mathbb{Z}_2^7$ | 128 | 8 | **Solved** | 0 |
| Diamond | $ | 256 | 4 | **Solved** | 0 |

### Analysis
1. **P1 Breakthrough**: The k=4, m=4 problem was solved using Fiber-Structured SA. This confirms that even-m parity is resolvable for even k.
2. **Equivariant moves**: Flipping entire orbits (symmetry blocks) reaches score-9 fast but plateaus there without deep basin escapes.
3. **Non-Abelian Parity**: We have formally extended the parity obstruction $γ_2$ to non-abelian central extensions. Both the Binary Icosahedral group (2I) and Heisenberg group ((\mathbb{Z}_6)$) are proven impossible for k=3.

## Remote Execution
Searches are offloaded to Kaggle using `kaggle_search.py` and monitored via:
```bash
python engine.py --remote
```
