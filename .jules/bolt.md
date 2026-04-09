
## 2026-05-18 - Vectorization of Cleanup Gate & RFFT Transition
**Learning:** Linear searching through large HRR registries in Python is a massive bottleneck (measured ~0.7s for 100 calls on 1500 items). Vectorizing with `np.dot` provides immediate ~36% speedup for cleanup and ~45% for queries by offloading O(N*D) search to BLAS. Transitioning to `rfft`/`irfft` for real-valued signals reduces computation by ~42%.
**Action:** Always prefer matrix-vector products over Python loops for high-dimensional similarity searches in TGI/HRR manifolds.

## 2026-05-18 - Wide-Scale Optimization: Bucket Caching & Batch Ingestion
**Learning:** Sequential Disk I/O and repetitive file locking are the primary bottlenecks in large-scale HRR manifold operations. Implementing an LRU Bucket Cache reduces query latency by ~27% for repeated accesses. Vectorizing the ingestion pipeline (using batch FFTs) and grouping writes by bucket provides a ~52% speedup for bulk operations.
**Action:** Use batching for all bulk logic population tasks. Implement caching at the bucket level to mitigate the cost of high-dimensional superposition retrievals.
