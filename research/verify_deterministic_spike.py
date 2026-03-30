import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma, verify_sigma

def test_odd_m():
    print("Verifying Deterministic Spike Construction for Odd m...")
    for m in [3, 5, 7, 9, 11, 13, 15]:
        sol = construct_spike_sigma(m, 3)
        if sol and verify_sigma(sol, m):
            print(f"  [PASS] m={m} verified.")
        else:
            print(f"  [FAIL] m={m} failed.")
            if sol:
                # Debug info
                n = m**3
                for c in range(3):
                    vis = set(); cur = (0,0,0)
                    for _ in range(n):
                        if cur in vis: break
                        vis.add(cur)
                        p = sol.get(cur)
                        arc = p[c]
                        nxt = list(cur); nxt[arc] = (nxt[arc] + 1) % m
                        cur = tuple(nxt)
                    print(f"    Color {c}: len={len(vis)} {'(Hamiltonian)' if len(vis)==n else ''}")
    print("Verification complete.")

if __name__ == "__main__":
    test_odd_m()
