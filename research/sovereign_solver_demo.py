import sys, os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import solve, verify_sigma, Weights

def demo():
    print("╔═══════════════════════════════════════════════╗")
    print("║      SOVEREIGN FSO MASTER SOLVER DEMO         ║")
    print("╚═══════════════════════════════════════════════╝")

    # 1. CANONICAL GOLDEN PATH (Odd m, k=3)
    m_odd = 25
    print(f"\n[1] CANONICAL GOLDEN PATH: m={m_odd}, k=3")
    print(f"    Expected: O(m) Deterministic Construction")
    t0 = time.perf_counter()
    sol = solve(m_odd, 3)
    t1 = time.perf_counter()
    print(f"    Construction Time: {(t1-t0)*1000:.3f}ms")

    if sol:
        print(f"    Verifying m^3={m_odd**3} vertices...")
        v0 = time.perf_counter()
        valid = verify_sigma(sol, m_odd)
        v1 = time.perf_counter()
        print(f"    Verification Result: {'PASSED' if valid else 'FAILED'} ({(v1-v0)*1000:.3f}ms)")
    else:
        print("    [!] Failed to construct solution.")

    # 2. PARITY OBSTRUCTION (Even m, k=3)
    m_even = 26
    print(f"\n[2] PARITY OBSTRUCTION: m={m_even}, k=3")
    print(f"    Expected: O(1) Absolute Block")
    try:
        t0 = time.perf_counter()
        solve(m_even, 3)
        print("    [!] Error: Obstruction not detected.")
    except Exception as e:
        t1 = time.perf_counter()
        print(f"    Caught: {e}")
        print(f"    Detection Time: {(t1-t0)*1000:.6f}ms")

    # 3. NON-CANONICAL SOLVABILITY (Even m, Even k)
    print(f"\n[3] NON-CANONICAL SOLVABILITY: m=4, k=4")
    print(f"    Expected: SA Fallback (Heuristic)")
    t0 = time.perf_counter()
    # Tiny iteration limit for demo
    sol = solve(4, 4, max_iter=100)
    t1 = time.perf_counter()
    print(f"    SA Call Time: {(t1-t0)*1000:.3f}ms")
    print(f"    Status: {'Solution Found' if sol else 'Search Continued (limit reached)'}")

    print("\n" + "═"*50)
    print("  FOUNDATIONS OF FSO: COMPLETE")
    print("═"*50)

if __name__ == "__main__":
    demo()
