import sys

def get_fiber(pos, m):
    return sum(pos) % m

def calculate_next_hop(current, color, m):
    x, y, z = current
    s = get_fiber(current, m)

    b = 0
    if s == 0:
        if color == 0: b = 2
        else:          b = -(m - 1)

    if color == 0: return ((x + 1 + b) % m, (y - b) % m, z % m)
    if color == 1: return (x % m, (y + 1 + b) % m, (z - b) % m)
    if color == 2: return ((x - b) % m, y % m, (z + 1 + b) % m)
    return current

def check_m(m):
    print(f"--- Checking m={m} ---")
    for color in range(3):
        vis = set()
        cur = (0, 0, 0)
        for _ in range(m**3):
            if cur in vis:
                print(f"  Color {color} FAILED: Repeated node {cur} at step {_}")
                return False
            vis.add(cur)
            cur = calculate_next_hop(cur, color, m)
        if len(vis) != m**3:
            print(f"  Color {color} FAILED: Visited only {len(vis)} nodes")
            return False
        if cur != (0, 0, 0):
            print(f"  Color {color} FAILED: Did not return to origin, ended at {cur}")
            return False
        print(f"  Color {color} PASSED (Hamiltonian)")

    # Check edge disjointness
    all_edges = [set() for _ in range(3)]
    for color in range(3):
        cur = (0, 0, 0)
        for _ in range(m**3):
            nxt = calculate_next_hop(cur, color, m)
            # Use directed edges because Hamiltonian cycles are directed
            edge = (cur, nxt)
            all_edges[color].add(edge)
            cur = nxt

    for i in range(3):
        for j in range(i + 1, 3):
            isect = all_edges[i].intersection(all_edges[j])
            if isect:
                print(f"  Colors {i} and {j} overlap at {len(isect)} edges")
            else:
                print(f"  Colors {i} and {j} are edge-disjoint")
    return True

if __name__ == "__main__":
    for m in [3, 5, 7]:
        check_m(m)
