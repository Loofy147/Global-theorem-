import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import solve, verify_sigma

def verify_all():
    ms = [3, 5, 7, 9, 11, 13, 15]
    all_ok = True
    for m in ms:
        print(f"Testing m={m:2d} (O(m) direct construction)...")
        sol = solve(m, k=3)
        if sol is None:
            print(f"  m={m:2d}: FAILED - No solution found")
            all_ok = False
            continue
        valid = verify_sigma(sol, m)
        if valid:
            print(f"  m={m:2d}: PASSED")
        else:
            print(f"  m={m:2d}: FAILED - Invalid Hamiltonian decomposition")
            all_ok = False

    if all_ok:
        print("-" * 60)
        print("ALL TESTS PASSED - Generalized spike construction verified.")
    else:
        print("-" * 60)
        print("SOME TESTS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    verify_all()
