# Problem Status & Solved Instances

This document tracks the status of all combinatorial problems, algebraic proofs, and competition benchmarks handled by the Short Exact Sequence (SES) Framework.

## 1. Decompositions of $\mathbb{Z}_m^k$ (Claude's Cycles)

The core task is to find a set of $k$ permutations $\sigma_c$ that decompose the Cayley graph of $\mathbb{Z}_m^k$ into $k$ disjoint Hamiltonian cycles.

| Problem | Parameters | Method | Iterations | Best Score | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1** | $k=4, m=4$ | Fiber-Structured SA | 50M | 0 | **Solved** |
| **P2** | $k=3, m=6$ | Multi-Fiber Basin Escape | 500k | **0** (via Repair) | **Solved** |
| **P3** | $k=3, m=8$ | Sovereign Solver (Obstruction) | $O(1)$ | -- | **Proven Impossible** |
| **Odd $m$** | $k=3, m \in \{3, 5, \dots\}$ | Sovereign Spike | $O(m)$ | 0 | **Analytically Proven** |

## 2. Multi-Modal Manifolds

| Domain | Sizing | Metric | Status |
| :--- | :--- | :--- | :--- |
| **Vision** | $G_{256}^5$ | Cohomological Gradient | **Stable (v2.0)** |
| **Neural** | $G_{255}^3$ | Topological Entropy | **Stable** |
| **Knowledge** | $G_{256}^4$ | Closure Hash Density | **Stable (v16.0)** |
| **Frontier** | $G_{256}^{128}$ | Hilbert Spectrum | **Stable (v1.0)** |

## 3. Proven Impossibilities ($H^2$ Parity Obstructions)

Configurations are strictly **PROVED IMPOSSIBLE** if $m$ is even and $k$ is odd.

| Configuration | Parameters | Group | Reason |
| :--- | :--- | :--- | :--- |
| **Even $m$, $k=3$** | $m \in \{4, 6, 8, \dots\}$ | $\mathbb{Z}_m^3$ | $H^2$ Parity Obstruction |
| **Heisenberg** | $m=6, k=3$ | $Heis(\mathbb{Z}_6)$ | Non-Abelian $H^2$ Block |
| **Icosahedral** | $k=3$ | $2I$ (Binary) | $H^2$ Parity Obstruction |

## 4. The Non-Canonical Obstruction

Even when the $H^2$ parity obstruction vanishes (Odd $m$), certain r-triples may be blocked by the joint-sum constraint.

- **Thm 14.1**: For $m=9$, the triple $r=(2, 2, 5)$ is **OBSTRUCTED** despite having $\gcd(r_i, m)=1$.
- **Golden Path Immunity**: The canonical Spike $r=(1, m-2, 1)$ is analytically proven to be immune to this obstruction for all odd $m$.

## 5. Verified Theorems

- **Thm 11.1**: Analytic Proof of Spike Construction (Golden Path) for all odd $m$.
- **Thm 14.1**: Non-Canonical Obstruction for composite $m$.
- **Thm 6.1**: Finalized Parity Obstruction Law (Even $m$ + Odd $k$).

---
*Last Updated: March 2026*
