import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma, verify_sigma

def test():
    sol = construct_spike_sigma(3, 3)
    if sol:
        m = 3
        n = m**3
        for c in range(3):
            vis = set(); cur = (0,0,0)
            for _ in range(n):
                if cur in vis: break
                vis.add(cur); p = sol.get(cur)
                arc_type = p[c]; next_v = list(cur)
                next_v[arc_type] = (next_v[arc_type] + 1) % m
                cur = tuple(next_v)
            print(f"Cycle {c}: {len(vis)} steps, final {cur}")
        print("verify_sigma says:", verify_sigma(sol, 3))

test()
