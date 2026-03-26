import math

def count_f2024_values():
    """
    f(m) + f(n) = f(m + n + mn)
    f(n) = \sum a_p * v_p(n+1)
    a_p = f(p-1) >= 1
    Constraint: f(n) <= 1000 for n <= 1000.
    Find number of values for f(2024) = h(2025) = 4*a_3 + 2*a_5.
    """
    values = set()
    # 3^6 = 729 <= 1001, so 6*a_3 <= 1000
    # 5^4 = 625 <= 1001, so 4*a_5 <= 1000
    # 3^4 * 5 = 405 <= 1001, so 4*a3 + a5 <= 1000
    # 3^2 * 5^2 = 225 <= 1001, so 2*a3 + 2*a5 <= 1000
    # 3 * 5^3 = 375 <= 1001, so a3 + 3*a5 <= 1000
    # Also 3^4 * 5 * 2 = 810 <= 1001, but we can set a2=1 (min).
    # The condition is: there exists {a_p >= 1} such that max_{n<=1000} f(n) <= 1000.
    # The tightest constraint on (a3, a5) is when all other a_p = 1.
    # Then for any x = 3^i * 5^j * 2^k * p1^e1... <= 1001,
    # i*a3 + j*a5 + k*a2 + e1*a_p1 ... <= 1000.
    # This is i*a3 + j*a5 + (k + e1 + ...) <= 1000.
    # Let S(i,j) = max { k + e1 + ... : 2^k * p1^e1 ... <= 1001 / (3^i * 5^j) }.
    # Since a_p >= 1, to minimize the sum, we pick p=2 (smallest).
    # So S(i,j) = floor(log2(1001 / (3^i * 5^j))).

    memo_S = {}
    def get_S(i, j):
        if (i, j) in memo_S: return memo_S[(i, j)]
        limit = 1001 // (3**i * 5**j)
        if limit < 1: return None
        res = 0
        if limit >= 2:
            res = int(math.log2(limit))
        memo_S[(i, j)] = res
        return res

    for a3 in range(1, 167): # 6*a3 <= 1000
        for a5 in range(1, 251): # 4*a5 <= 1000
            possible = True
            for i in range(7): # 3^6 = 729
                for j in range(5): # 5^4 = 625
                    if i == 0 and j == 0: continue
                    S = get_S(i, j)
                    if S is None: continue
                    if i*a3 + j*a5 + S > 1000:
                        possible = False
                        break
                if not possible: break

            if possible:
                values.add(4*a3 + 2*a5)

    return sorted(list(values))

if __name__ == "__main__":
    vals = count_f2024_values()
    print(f"Number of values: {len(vals)}")
    print(f"Min: {min(vals)}, Max: {max(vals)}")
