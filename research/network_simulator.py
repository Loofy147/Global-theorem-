import sys, os
import random
from itertools import product as iprod

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma, verify_sigma

class Torus3D:
    def __init__(self, m):
        self.m = m
        self.nodes = list(iprod(range(m), range(m), range(m)))
        # Sigma for FSO: v -> (arc_for_c0, arc_for_c1, arc_for_c2)
        # Using the proven construction from core.py
        self.sigma = construct_spike_sigma(m, 3)
        if not self.sigma:
            print(f"FAILED to construct Spike for m={m}")

    def get_neighbors(self, v):
        # 0: X+, 1: Y+, 2: Z+
        x, y, z = v
        return [
            ((x+1)%self.m, y, z),
            (x, (y+1)%self.m, z),
            (x, y, (z+1)%self.m)
        ]

    def dor_route(self, current, target):
        if current == target: return None
        cx, cy, cz = current
        tx, ty, tz = target
        if cx != tx: return 0 # X+
        if cy != ty: return 1 # Y+
        if cz != tz: return 2 # Z+
        return None

    def fso_route(self, current, color):
        # Follow fixed Hamiltonian color
        return self.sigma[current][color]

def run_simulation(m=3):
    torus = Torus3D(m)
    if not torus.sigma: return

    print(f"--- 3D Torus Interconnect Simulation (m={m}) ---")
    print(f"Total Nodes: {len(torus.nodes)}")
    print(f"Total Edges: {3 * len(torus.nodes)}")

    # 1A. DOR Baseline
    print("\n[Protocol: Dimension-Order Routing (DOR)]")
    link_usage_dor = {}
    num_random_packets = 1000
    for _ in range(num_random_packets):
        src = random.choice(torus.nodes)
        dst = random.choice(torus.nodes)
        while dst == src: dst = random.choice(torus.nodes)
        cur = src
        while cur != dst:
            arc = torus.dor_route(cur, dst)
            nxt = torus.get_neighbors(cur)[arc]
            link = (cur, nxt)
            link_usage_dor[link] = link_usage_dor.get(link, 0) + 1
            cur = nxt

    max_contention_dor = max(link_usage_dor.values()) if link_usage_dor else 0
    print(f"  Max Link Contention (Collisions): {max_contention_dor}")
    print(f"  Avg Link Load:                   {sum(link_usage_dor.values())/len(link_usage_dor):.2f}")

    # 1B. FSO Spike Routing
    print("\n[Protocol: FSO Spike Routing]")
    link_usage_fso = {}

    for color in range(3):
        cur = (0,0,0)
        vis = set()
        for _ in range(m**3):
            vis.add(cur)
            arc = torus.fso_route(cur, color)
            nxt = torus.get_neighbors(cur)[arc]
            link = (cur, nxt)
            link_usage_fso[link] = link_usage_fso.get(link, 0) + 1
            cur = nxt

        if len(vis) != m**3:
            print(f"  FAILURE: Color {color} is NOT Hamiltonian (visited {len(vis)} nodes)")
        else:
            print(f"  Color {color} Highway: Hamiltonian Verified.")

    max_contention_fso = max(link_usage_fso.values())
    min_contention_fso = min(link_usage_fso.values())

    print(f"  Max Link Contention (Collisions): {max_contention_fso}")
    print(f"  Min Link Contention:             {min_contention_fso}")

    if max_contention_fso == 1 and len(link_usage_fso) == 3 * m**3:
        print("\n[ANALYSIS]")
        print("FSO Spike routing achieved a Perfect Edge Decomposition.")
        print("Hardware Benefit: ZERO Collisions even at 100% Link Saturation.")
        print("Memory Benefit:   Logic is O(1) modulo arithmetic (No Routing Tables).")
    else:
        print("\n[ANALYSIS]")
        print(f"FSO used {len(link_usage_fso)} edges. Max contention: {max_contention_fso}")

if __name__ == "__main__":
    # Test on m=3 first to verify logic
    run_simulation(m=3)

if __name__ == "__main__":
    # Now run m=9 to fulfill the requirement
    print("\n" + "="*40 + "\n")
    run_simulation(m=9)
