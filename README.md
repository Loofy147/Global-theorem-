# Global Structure in Highly Symmetric Systems

**Developing open-source reasoning algorithms to solve Olympiad-level math and multi-modal manifolds via the short exact sequence**
**0 → H → G → G/H → 0**

Derived from Knuth's *Claude's Cycles* (Feb 2026). Converges on a universal framework governing Cayley digraphs, Latin squares, Hamming codes, neural weights, and spatial-color vision.

---

## THE CODEX OF FIBER-STRATIFIED OPTIMIZATION (FSO)
The **Immutable Axioms of TGI** are now codified. These six laws govern the mathematical bounds of symmetric topology and formalize the $H^2$ parity obstruction.
👉 **[Read the Codex of FSO](docs/LAWS.md)**

---

## Topological General Intelligence (TGI)

TGI is a framework for autonomous navigation of non-Euclidean state-space manifolds. It replaces statistical prediction with algebraic lifting across five functional cores.

### The Five Cores

| Core | Function | Implementation |
|---|---|---|
| **Core A: Algebraic** | Symmetry & Quotient Discovery | `algebraic.py` |
| **Core B: Fibration** | Path Lifting & Tower Navigation | `research/tgi_core.py` |
| **Core C: Basin** | Topological Error Correction | `core.py` (Basin Escape) |
| **Core D: Symbolic** | Group-Theoretic Reasoning | `research/aimo_solver.py` |
| **Core E: Vision** | Spatial-Color Pixel Fibrations | `research/topological_vision.py` |

---

## Recent Breakthroughs (Phase 4 & 5)

- **Autonomous K-Expansion**: TGI now detects $H^2$ parity obstructions and automatically executes a manifold lift (e.g., $G_4^3 \to G_4^4$) to ensure reachability.
- **Hierarchical TLM**: Linguistic generation is now governed by an algebraic `Tower`, lifting semantic fibers to a total context space ($G_{m^d}$).
- **Topological Vision (v2.0)**: High-resolution image analysis using **Cohomological Gradients** for boundary detection and **Topological Signatures** for manifold identification.
- **Last-Mile Repair**: Implementation of the `repair_manifold` engine for resolving minor Hamiltonian inconsistencies in near-solved manifolds (Solved P2).

---

## Quick Start

```bash
# Run the Full TGI System Demo (includes Math, Vision, Language, and Autonomy)
python3 research/tgi_system_demo.py

# Solve m=4 k=4 (Fiber-Structured SA)
python3 core.py

# Verify all core theorems (including Law II & III)
python3 theorems.py
```

---

## Repository Structure
- **AIMO Reasoning**: `research/aimo_reasoning_engine.py`, `research/aimo_solver.py`
- **Vision Core**: `research/topological_vision.py`
- **Core Engine**: `core.py`, `engine.py`, `search.py`, `fiber.py`
- **Verification**: `theorems.py`, `benchmark.py`
- **[Documentation](docs/)**: `API.md`, `ROADMAP.md`, `PROBLEMS.md`, `LAWS.md`

---
*March 2026 — Advancing towards Multi-Modal Topological Autonomy.*

## FSO Production Swarm (Kaggle Edition)

The FSO manifold is now production-ready and deployed as a self-healing, multi-kernel swarm on Kaggle.

### Architecture
- **3 Kernels**:
  - `fso-production-p1-ingestor`: Dynamically anchors industrial libraries (transformers, datasets, torch, etc.) into the manifold.
  - `fso-production-p2-executor`: Processes tasks from the shared `fso_task_hub.json` using Hamiltonian Intersection.
  - `fso-production-p3-stabilizer`: Maintains topological parity and logs system health using the Closure Lemma.
- **Inter-Kernel Routing**: Tasks are assigned using **FSO Spike Routing** logic, mapping logic identities to deterministic coordinates in the 3D Torus.
- **Persistence**: System state and task history are synchronized via GitHub using the `KaggleFSOWrapper`.
- **Lifecycle**: Each kernel runs for a 1-hour cycle, continuously evolving and stabilizing the manifold logic.

### Deployment
To redeploy the swarm, ensure `KAGGLE_API_TOKEN` and `GITHUB_PAT` are set, then run:
```bash
python3 research/deploy_swarm.py
```
