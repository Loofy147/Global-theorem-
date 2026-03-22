# Global Structure in Highly Symmetric Systems

**Finding global structure in combinatorial problems via the short exact sequence**  
**0 → H → G → G/H → 0**

Derived from Knuth's *Claude's Cycles* (Feb 2026). Converges on a universal framework governing Cayley digraphs, Latin squares, Hamming codes, magic squares, difference sets, and Pythagorean triples.

---

## Repository Structure

- **Core Engine**: `core.py`, `engine.py`, `search.py`, `fiber.py`
- **Verification**: `theorems.py`, `benchmark.py`
- **Open Frontiers**: `frontiers.py`, `solutions.py`
- **[Documentation](docs/)**: `API.md`, `CLOSURE_LEMMA.md`
- **[Research Lab](research/)**: Papers (English/Arabic), Methodology, Experimental scripts

---

## Quick Start

```bash
# Prove m=4 k=3 impossible in 0.02ms
python core.py

# Run all 10 theorems
python theorems.py

# Analyse any domain
python engine.py

# Check open problems
python frontiers.py --status

# Benchmark
python benchmark.py --quick
```

---

## The Four Coordinates

Every highly symmetric combinatorial problem reduces to the short exact sequence:

```
0  →  H  →  G  →  G/H  →  0
```

| Coordinate | Abstract | In Claude's Cycles | Cohomology |
|---|---|---|---|
| **C1 Fiber Map** | φ: G → G/H | f(i,j,k) = (i+j+k) mod m | H⁰ |
| **C2 Twisted Translation** | Q_c(h) = h + g_c | Q_c(i,j) = (i+b_c(j), j+r_c) | H¹ 1-cocycle |
| **C3 Governing Condition** | gcd(r_c, \|G/H\|) = 1 | r-triple (1, m−2, 1) | H¹ class ≠ 0 |
| **C4 Parity Obstruction** | arithmetic of \|G/H\| | 3 odds ≠ even m | H²(Z₂,Z/2) = Z/2 |

---

## The 8 Weights

For any problem (m, k), these 8 values fully determine solvability, strategy, and solution count. All computed in **O(m²) or faster**.

| Weight | Formula | What it gives |
|---|---|---|
| W1 H² obstruction | `all_odd AND k_odd AND m_even` | Proves impossible in O(1) |
| W2 r-tuple count | `\|{t ∈ cp^k : sum=m}\|` | Number of construction seeds |
| W3 canonical seed | `(1,...,1, m-(k-1))` | Direct construction path |
| W4 H¹ order **exact** | `φ(m)` (Euler totient) | Gauge multiplicity |
| W5 search exponent | `m × log₂(valid_levels)` | log of compressed space |
| W6 compression | W5 / (m³ × log₂(6)) | Search space reduction |
| W7 solution lb | `φ(m) × (m^(m-1)·φ(m))^(k-1)` | `\|M_k(G_m)\|` lower bound |
| W8 orbit size | `m^(m-1)` | Solutions per gauge class |

---

## Theorems (all 10 verified)

| Theorem | Statement | Verified |
|---|---|---|
| **3.2** Orbit-Stabilizer | \|Z_m³\| = m × m² | m=2..11 |
| **5.1** Single-Cycle | Q_c is m²-cycle iff gcd(r,m)=1 AND gcd(Σb,m)=1 | 8 cases |
| **6.1** Parity Obstruction | Even m, odd k → column-uniform impossible | m=4..16 |
| **7.1** Odd m Existence | r-triple (1,m−2,1) valid for all odd m≥3 | m=3..15 |
| **8.2** m=4 Solution | Explicit 64-vertex 3-Hamiltonian decomposition | verified |
| **9.1** k=4 Resolution | (1,1,1,1) breaks even-m obstruction for m=4 | verified |
| **Cor 9.2** Classification | Even m: odd k blocked, even k feasible | 7 cases |
| **10.1** Fiber-Uniform | No fiber-uniform σ for k=4, m=4 (exhaustive) | 331,776 cases |
| **Moduli** Torsor | M_k(G_m) is a torsor under H¹(Z_m,Z_m²) | m=3: 648 = 2×18² |
| **W4** H¹ exact | \|H¹\| = φ(m), not the v1.0 approximation | m=3,4,5 |

---

## Benchmark

v2.1 vs 6 alternatives on 6 problems (10s timeout):

| Solver | Correct | Proves ⊘ | Avg ms | Timeouts |
|---|---|---|---|---|
| **v2.1 Basin-escape** | **6/6** | **3** | **360** | **0** |
| A3 v1.0 pipeline | 5/6 | 2 | 39 | 1 |
| A4 level enum | 3/6 | 0 | 2,124 | 3 |
| A2 backtrack | 3/6 | 0 | — | 3 |
| A1 pure SA | 1/6 | 0 | 6,909 | 3 |
| A0 brute random | 0/6 | 0 | — | 6 |
| A5 scipy | 0/6 | 0 | 297 | 0 |

**Key advantage (v2.1 Basin-escape):** Breaks deep Z3-periodic local minima. Record score=4 for P2.

Geometric mean speedup: **38,120×** over pure SA, **7,203×** over level enumeration.

---

## Open Problems

| Problem | Status | Known |
|---|---|---|
| P1: k=4, m=4 construction | 🔴 OPEN | Score 337→230 in 300K iters. Record: 230. Basin-escape v2.1 ready. |
| P2: m=6, k=3 full-3D | 🔴 OPEN | New record: score=4 in 8M iters via Basin-escape v2.1 adaptive kicks. |
| P3: m=8, k=3 full-3D | 🔴 OPEN | First attempt. 512 vertices. |
| P4: W7 formula | 🟢 RESOLVED | phi(m)×coprime_b^(k-1). Exact m=3, lower bound m≥5. |
| P5: Non-abelian (S_3) | 🟢 RESOLVED | Same parity law. k=2 feasible, k=3 blocked. |
| P6: Product Z_m×Z_n | 🟢 RESOLVED | Fiber quotient = Z_gcd(m,n). Framework complete. |
| Closure lemma | 🟡 PARTIAL | Proved m=3 exhaustively. General algebraic proof open. |

---

## Papers (see [research/](research/))

- **Global Structure in Highly Symmetric Systems** (English, 19pp)
- **The Even-m Case in Claude's Cycles** (English, 5pp)
- **حالة m الزوجية في مسألة دورات كلود** (Arabic, 6pp)

---

*March 2026*
