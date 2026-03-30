from core import run_hybrid_sa
sol, info = run_hybrid_sa(3, 3, seed=42, max_iter=5000)
print(f"Sol found: {sol is not None}, Best score: {info['best']}")
