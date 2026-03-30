import sys, os
from math import gcd

def verify_construction(m):
    # ID  = (0, 1, 2)
    # S12 = (0, 2, 1)
    # S01 = (1, 0, 2)

    N = [[0, 0, 0] for _ in range(3)]

    # ID: m-2 levels
    for _ in range(m-2):
        N[0][0] += 1
        N[1][1] += 1
        N[2][2] += 1
    # S12: 1 level
    N[0][0] += 1
    N[2][1] += 1
    N[1][2] += 1
    # S01: 1 level
    N[1][0] += 1
    N[0][1] += 1
    N[2][2] += 1

    print(f"m={m}")
    for c in range(3):
        r = N[c][1]
        sum_b = (N[c][2] - N[c][0]) % m
        ok_r = gcd(r, m) == 1
        ok_b = gcd(sum_b, m) == 1
        print(f"  Color {c}: r={r} ({'OK' if ok_r else 'FAIL'}), sum_b={sum_b} ({'OK' if ok_b else 'FAIL'})")
        if not (ok_r and ok_b): return False
    return True

for m in [3, 5, 7, 9, 11]:
    if not verify_construction(m):
        print(f"FAILED for m={m}")
        break
else:
    print("SUCCESS for all tested m")
