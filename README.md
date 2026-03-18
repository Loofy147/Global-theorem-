# claudecycles

**Discovery system for Knuth's "Claude's Cycles" problem** (Feb 2026).

Consolidates every script used to study, discover patterns in, and solve the problem of decomposing the arcs of the m³-vertex digraph into 3 directed Hamiltonian cycles.

## Quick start

```bash
# Verify hardcoded solutions
python -m claudecycles verify 3
python -m claudecycles verify 5

# Find and verify a new solution
python -m claudecycles solve 7
python -m claudecycles solve 9

# Deep mathematical analysis
python -m claudecycles analyze 3

# All four theorems
python -m claudecycles theorem

# Cross-m comparison
python -m claudecycles compare 3 5 7 9
```

## Python API

```python
from claudecycles import (
    get_solution,          # hardcoded verified solutions (m=3,5)
    construct_for_odd_m,   # constructive algorithm for any odd m>2
    find_sigma,            # unified search (auto strategy)
    verify_sigma,          # full verification
    SolutionAnalysis,      # deep Q structure / theorem analysis
)

# Get and verify
sigma = get_solution(3)
result = verify_sigma(sigma, 3)
print(result)     # ✅ m=3: Valid 3-Hamiltonian decomposition

# Deep analysis
a = SolutionAnalysis(sigma, 3).run()
print(a.report())

# Find new solution for odd m
sigma7 = construct_for_odd_m(7)
print(verify_sigma(sigma7, 7))

# Even m: must use SA (fiber approach provably fails)
sigma4 = find_sigma(4, strategy='sa', max_iter=500_000)
```

## Module map

| File | Purpose |
|------|---------|
| `core.py` | Digraph definition, verification, arc tracing |
| `fiber.py` | Fiber decomposition, Q composition, theorem checks |
| `search.py` | RandomSearch · BacktrackSearch · SimulatedAnnealing |
| `analysis.py` | SolutionAnalysis, dependency detection, cross-m compare |
| `solutions.py` | Hardcoded m=3,5; `construct_for_odd_m` |
| `cli.py` | Command-line interface |

## Key theorems proved

1. **Twisted Translation**: `Q_c(i,j) = (i + b_c(j), j + r_c) mod m`
2. **Single-Cycle Conditions**: `gcd(r_c, m) = 1` AND `gcd(Σb_c, m) = 1`
3. **Existence for odd m**: Valid `(r_0,r_1,r_2)=(1, m-2, 1)` always works
4. **Impossibility for even m**: Sum of 3 odd numbers is odd ≠ even = m ✓
