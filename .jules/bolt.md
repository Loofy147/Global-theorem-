
## 2026-05-18 - Vectorization of Cleanup Gate & RFFT Transition
**Learning:** Linear searching through large HRR registries in Python is a massive bottleneck (measured ~0.7s for 100 calls on 1500 items). Vectorizing with `np.dot` provides immediate ~36% speedup for cleanup and ~45% for queries by offloading O(N*D) search to BLAS. Transitioning to `rfft`/`irfft` for real-valued signals reduces computation by ~42%.
**Action:** Always prefer matrix-vector products over Python loops for high-dimensional similarity searches in TGI/HRR manifolds.
