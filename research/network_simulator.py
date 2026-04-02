import sys, os
import random
from itertools import product as iprod, permutations

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma, verify_sigma

class Torus3D:
    def __init__(self, m):
        self.m = m
        self.nodes = list(iprod(range(m), range(m), range(m)))
        self.sigma = construct_spike_sigma(m, 3)
        self.dim_orders = list(permutations(range(3)))

    def get_neighbors(self, v):
        x, y, z = v
        return [
            ((x+1)%self.m, y, z),
            (x, (y+1)%self.m, z),
            (x, y, (z+1)%self.m)
        ]

    def dor_route(self, current, target, order=(0, 1, 2)):
        if current == target: return None
        for dim in order:
            if current[dim] != target[dim]:
                return dim
        return None

    def fso_route(self, current, color):
        return self.sigma[current][color]

def run_simulation(m=7): # Reducing m to 5 for faster execution in sandbox
    torus = Torus3D(m)
    if not torus.sigma: return

    print(f"--- 3D Torus Hardware Benchmark (m={m}) ---")
    print(f"Scenario: Triple Full-Throughput Broadcasts (1 per Hamiltonian Highway)")

    protocols = ["DOR", "O1TURN", "ROMM", "FSO (Spike)"]

    for proto in protocols:
        link_usage = {}

        for color in range(3):
            src = (color, color, color)
            if proto == "FSO (Spike)":
                cur = src
                for _ in range(m**3):
                    arc = torus.fso_route(cur, color)
                    nxt = torus.get_neighbors(cur)[arc]
                    link = (cur, nxt)
                    link_usage[link] = link_usage.get(link, 0) + 1
                    cur = nxt
            else:
                # Optimized simulation for standard protocols
                for dst in torus.nodes:
                    if dst == src: continue
                    cur = src
                    random.seed(color + 42)
                    order = (0, 1, 2)
                    if proto == "O1TURN": order = random.choice(torus.dim_orders)

                    # For ROMM, we'll pick mid node and route in two phases
                    if proto == "ROMM":
                        mid = tuple(random.randint(min(src[i], dst[i]), max(src[i], dst[i])) if src[i] != dst[i] else src[i] for i in range(3))
                        # Phase 1: src -> mid
                        while cur != mid:
                            arc = torus.dor_route(cur, mid)
                            nxt = torus.get_neighbors(cur)[arc]
                            link = (cur, nxt)
                            link_usage[link] = link_usage.get(link, 0) + 1
                            cur = nxt
                        # Phase 2: mid -> dst
                        while cur != dst:
                            arc = torus.dor_route(cur, dst)
                            nxt = torus.get_neighbors(cur)[arc]
                            link = (cur, nxt)
                            link_usage[link] = link_usage.get(link, 0) + 1
                            cur = nxt
                    else: # DOR and O1TURN
                        while cur != dst:
                            arc = torus.dor_route(cur, dst, order)
                            nxt = torus.get_neighbors(cur)[arc]
                            link = (cur, nxt)
                            link_usage[link] = link_usage.get(link, 0) + 1
                            cur = nxt

        max_contention = max(link_usage.values()) if link_usage else 0
        avg_load = sum(link_usage.values())/len(link_usage) if link_usage else 0
        print(f"| {proto:13} | Max Link Contention: {max_contention:4} | Avg Load: {avg_load:7.2f} |")

if __name__ == "__main__":
    run_simulation(m=7)
