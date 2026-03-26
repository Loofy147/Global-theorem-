# Kaggle Search Benchmarks

Results of high-budget combinatorial searches on Kaggle (March 2026).

## Decompositions of $\mathbb{Z}_m^k$

| Problem | Method | Iterations | Best Score | Status |
|---|---|---|---|---|
| **P1** (k=4, m=4) | Fiber SA (Basin v3.1) | 47.8M | 0 | **Solved** |
| **P2** (m=6, k=3) | Frontier SA (Basin v3.3) | 20M | 4 | Open |
| **P3** (m=8, k=3) | Frontier SA (Basin v3.3) | 10M | 15 | Open |

## Traveling Salesman Problem (TSP)

| Instance | Cities | Best Distance | Time |
|---|---|---|---|
| a280 | 150 | 583.95 | 1.27s |
| att48 | 48 | 873.62 | 2.10s |
| att532 | 150 | 482.47 | 0.94s |

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
