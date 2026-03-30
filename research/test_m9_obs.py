from math import gcd

def check_fso(m, r):
    possible_b = []
    for rc in r:
        limit = m - rc
        bs = [b for b in range(-limit, limit + 1) if abs(b) % 2 == limit % 2 and gcd(b, m) == 1]
        possible_b.append(bs)
        print(f"r={rc}, limit={limit}, bs={bs}")

    for b0 in possible_b[0]:
        for b1 in possible_b[1]:
            b2 = -b0 - b1
            if b2 in possible_b[2]:
                return True
    return False

m = 9
r = (2, 2, 5)
print(f"Result for m={m}, r={r}: {check_fso(m, r)}")
