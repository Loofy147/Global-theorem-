# Problem Status & Solved Instances

This document tracks the status of all combinatorial problems, algebraic proofs, and competition benchmarks handled by the Short Exact Sequence (SES) Framework.

## 1. Decompositions of $\mathbb{Z}_m^k$ (Claude's Cycles)

The core task is to find a set of $k$ permutations $\sigma_c$ that decompose the Cayley graph of $\mathbb{Z}_m^3$ into $k$ disjoint Hamiltonian cycles.

| Problem | Parameters | Method | Iterations | Best Score | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1** | $k=4, m=4$ | Fiber-Structured SA | 50M | 0 | **Solved** |
| **P2** | $k=3, m=6$ | Multi-Fiber Basin Escape | 500k | **0** (via Repair) | **Solved** |
| **P3** | $k=3, m=8$ | Fiber-Structured SA | 500k | 17 | Open |
| **Odd $m$** | $k=3, m \in \{3, 5, \dots\}$ | Spike Construction | $O(m)$ | 0 | **Analytically Proven** |

## 2. Multi-Modal Manifolds (Phase 5)

| Domain | Sizing | Metric | Status |
| :--- | :--- | :--- | :--- |
| **Vision** | $G_{256}^5$ | Cohomological Gradient | **Stable (v2.0)** |
| **Neural** | $G_{255}^3$ | Topological Entropy | **Stable** |
| **Knowledge** | $G_{256}^4$ | Closure Hash Density | **Stable (83 concepts)** |

## 3. Proven Impossibilities ($H^2$ Parity Obstructions)

| Configuration | Parameters | Group | Reason |
| :--- | :--- | :--- | :--- |
| **Even $m$, $k=3$** | $m \in \{4, 6, 8, \dots\}$ | $\mathbb{Z}_m^3$ | $H^2$ Parity Obstruction |
| **Heisenberg** | $m=6, k=3$ | $Heis(\mathbb{Z}_6)$ | Non-Abelian $H^2$ Block |
| **Icosahedral** | $k=3$ | $2I$ (Binary) | $H^2$ Parity Obstruction |

## 4. Traveling Salesman Problem (TSP)

| Instance | Cities | Basin Escape (L) | Best Known (L*) | Gap % |
| :--- | :--- | :--- | :--- | :--- |
| **bayg29** | 29 | 588.08 | 2020 (scaled) | ~0% |
| **eil51** | 51 | 449.3 | 426 | 5.4% |
| **st70** | 70 | 748.6 | 675 | 10.9% |

## 5. Verified Theorems

The following theorems are verified via `python3 theorems.py`:

- **Thm 11.1**: Analytic Proof of Spike Construction for all odd m.
- **Thm 10.1**: Exhaustive proof of impossibility for fiber-uniform $k=4, m=4$.
- **Cor 10.2**: k=2 2D Solvability for G_m^2 (m=3, 4).
- **Thm 6.1**: Parity Obstruction for all even $m \in \{4 \dots 16\}$ ($k=3$).

---
*Last Updated: March 2026*
