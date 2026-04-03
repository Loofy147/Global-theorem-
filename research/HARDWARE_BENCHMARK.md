# FSO Spike Routing: Hardware Interconnect Benchmark Results

## Executive Summary
In high-performance computing (HPC) and AI accelerator clusters (TPU Pods, GPU meshes), **All-to-All Broadcast** is a frequent and critical operation. Standard routing protocols (DOR, O1TURN, ROMM) fail to prevent link contention, leading to packet collisions, high latency, and the need for complex flow-control hardware.

**Fiber-Stratified Optimization (FSO)** leverages the **Spike Construction** to provide a deterministic, zero-collision Hamiltonian decomposition of the Torus graph.

## Benchmark Configuration
- **Topology**: 3D Torus (=7$, 343 nodes, 1029 edges)
- **Workload**: Triple concurrent full-throughput broadcasts (1 per Hamiltonian Highway)
- **Protocols**:
  - **DOR**: Dimension-Order Routing (Industry Standard)
  - **O1TURN**: Oblivious 1-turn (dimension order randomization)
  - **ROMM**: Randomized Oblivious Minimal Routing (2-phase)
  - **FSO (Spike)**: Deterministic Hamiltonian Decomposition

## Results Summary

| Protocol      | Max Link Contention | Avg Link Load | Contention Mitigation |
|---------------|---------------------|---------------|-----------------------|
| DOR           | 294                 | 19.02         | 0% (Baseline)         |
| O1TURN        | 299                 | 12.69         | 0%                    |
| ROMM          | 289                 | 12.43         | 2%                    |
| **FSO (Spike)** | **1**               | **1.00**      | **99.7%**             |

## Key Engineering Takeaways

### 1. Zero-Collision Property
While O1TURN and ROMM attempt to "spread" the load, they are ultimately limited by the stochastic nature of minimal routing. FSO Spike Routing is **structurally guaranteed** to be collision-free across its 3 disjoint highways. Even at 100% network saturation, contention remains exactly 1 packet per link.

### 2. O(1) Gate-Logic Routing
Unlike O1TURN or ROMM, which require random number generation and state tracking per packet, FSO Spike Routing is a simple, deterministic function of node coordinates:
-  \equiv (x+y+z) \pmod m$
- Routing Choice = (s, j)$
This logic can be hardwired into ASIC switches, requiring **zero RAM** for routing tables.

### 3. Latency vs. Throughput Trade-off
FSO follows a non-minimal Hamiltonian path. While individual packet latency (hop count) is higher than minimal routing for point-to-point traffic, its **aggregate throughput** for global broadcast operations is unbeatable, as it eliminates all queuing delays caused by link contention.
