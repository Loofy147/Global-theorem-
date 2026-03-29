from core import verify_sigma, SOLUTION_M4
print(f"Len: {len(SOLUTION_M4)}")
ok = verify_sigma(SOLUTION_M4, 4)
print(f"OK: {ok}")
if not ok:
    m = 4
    n = m**3
    for c in range(3):
        vis = set(); cur = (0,0,0)
        for i in range(n):
            if cur in vis:
                print(f"Cycle {c} repeated {cur} at step {i}")
                break
            vis.add(cur)
            p = SOLUTION_M4.get(cur)
            if not p:
                print(f"Cycle {c} missing key {cur}")
                break
            arc_type = p[c]
            next_v = list(cur)
            next_v[arc_type] = (next_v[arc_type] + 1) % m
            cur = tuple(next_v)
        else:
            if cur != (0,0,0):
                print(f"Cycle {c} did not return to origin, ended at {cur}")
            else:
                print(f"Cycle {c} VALID")
