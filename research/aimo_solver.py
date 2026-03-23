import sympy

def solve_alice_bob():
    # sA: Alice sweets, aA: Alice age
    # sB: Bob sweets, aB: Bob age
    sA, aA, sB, aB = sympy.symbols('sA aA sB aB', integer=True, positive=True)

    eq1 = sympy.Eq(sA + aA, 2 * (sB + aB))
    eq2 = sympy.Eq(sA * aA, 4 * (sB * aB))

    # "give me five of your sweets because then both our sum and product would be equal"
    # Alice sum: (sA-5) + aA, Bob sum: (sB+5) + aB
    # Alice product: (sA-5) * aA, Bob product: (sB+5) * aB
    eq3 = sympy.Eq((sA - 5) + aA, (sB + 5) + aB)
    eq4 = sympy.Eq((sA - 5) * aA, (sB + 5) * aB)

    sol = sympy.solve([eq1, eq2, eq3, eq4], [sA, aA, sB, aB])
    print(f"Alice & Bob Solution: {sol}")
    if sol:
        if isinstance(sol, list):
            for s in sol:
                print(f"  aA * aB = {s[1] * s[3]}")
        else:
            print(f"  aA * aB = {sol[aA] * sol[aB]}")

def solve_functional_equation():
    # f(m) + f(n) = f(m + n + mn)
    # Let g(x) = f(x-1). Then g(m+1) + g(n+1) = g((m+1)(n+1))
    # This is g(X) + g(Y) = g(XY) for X, Y > 1
    # This is a logarithmic functional equation: g(X) = c * log_b(X)
    # Since f: Z+ -> Z+, g: {2, 3, ...} -> Z+
    # g(n) = f(n-1). So f(n) = g(n+1) = c * log_b(n+1)
    # For f(n) to be an integer for all n, c * log_b(n+1) must be an integer.
    # This means n+1 must be a power of b, which isn't true for all n.
    # Wait, the domain is Z+, so f(1), f(2), ...
    # f(1) + f(1) = f(1+1+1) = f(3)
    # f(1) + f(3) = f(1+3+3) = f(7)
    # In general, f((2^k)-1) = k * f(1).
    # What about f(2)? f(1) + f(2) = f(1+2+2) = f(5).
    # Let x = m+1, y = n+1. Then f(x-1) + f(y-1) = f(xy-1).
    # Let h(x) = f(x-1). Then h(x) + h(y) = h(xy) for x, y in {2, 3, ...}.
    # h(x) = \sum a_p * v_p(x) where v_p(x) is the exponent of prime p in x.
    # f(n) = h(n+1) = \sum a_p * v_p(n+1).
    # Constraints: f(n) <= 1000 for n <= 1000.
    # f(2024) = h(2025). 2025 = 3^4 * 5^2.
    # So f(2024) = 4 * a_3 + 2 * a_5.
    # a_p are f(p-1). All a_p must be >= 0 (since f: Z+ -> Z+).
    # Since f(n) >= 1 (Z+), at least one a_p must be > 0.
    # For n <= 1000, n+1 <= 1001. Max prime < 1001 is 997.
    # f(p-1) = a_p. So a_p <= 1000.
    # For any x <= 1001, \sum a_p * v_p(x) <= 1000.
    # Specifically, a_p <= 1000 for all p <= 1001.
    # a_2 * v_2(x) <= 1000 => a_2 * 9 <= 1000 (since 2^9 = 512 < 1001) => a_2 <= 111.
    # a_3 * v_3(x) <= 1000 => a_3 * 6 <= 1000 (since 3^6 = 729 < 1001) => a_3 <= 166.
    # a_997 <= 1000.
    # f(2024) = 4 * a_3 + 2 * a_5.
    # What are the constraints on a_3 and a_5?
    # They must satisfy \sum a_p v_p(x) <= 1000 for all x <= 1001.
    # This is equivalent to:
    # a_2 * floor(log2(1001)) <= 1000
    # a_3 * floor(log3(1001)) <= 1000
    # ...
    # And also combinations like a_2 + a_3 + a_5 + a_7 <= 1000 (since 2*3*5*7 = 210 <= 1001).
    # 2*3*5*7*11 = 2310 > 1001.
    # So at most 4 distinct primes product can be <= 1001.
    # But a_p can be 0? The problem says f: Z+ -> Z+, so f(n) >= 1.
    # Thus a_p = f(p-1) must be >= 1 for all p.
    # If a_p >= 1, then f(2024) = 4*a_3 + 2*a_5.
    # Max a_3: 3^6 = 729 <= 1001, 3^7 = 2187 > 1001. So 6*a_3 <= 1000 => a_3 <= 166.
    # Max a_5: 5^4 = 625 <= 1001, 5^5 > 1001. So 4*a_5 <= 1000 => a_5 <= 250.
    # Also a_2+a_3+a_5+a_7 <= 1000. Since a_p >= 1, this is always possible if others are small.
    # The number of values f(2024) can take is the number of possible sums 4*a_3 + 2*a_5.
    # Wait, f(p-1)=a_p. p-1 is an integer. p is a prime.
    # For p=2, f(1)=a_2. For p=3, f(2)=a_3. For p=5, f(4)=a_5.
    # Is there any other constraint? f(m)+f(n)=f(m+n+mn) must hold for all m, n.
    # This implies f(n) = \sum a_p v_p(n+1) is the ONLY form.
    # And a_p = f(p-1).
    # Let's check: f(1) = a_2. f(2) = a_3. f(3) = h(4) = 2*a_2.
    # From f(1)+f(1)=f(3), we have a_2+a_2 = 2*a_2. Correct.
    # From f(1)+f(2)=f(5), we have a_2+a_3 = f(5) = h(6) = a_2+a_3. Correct.
    # So yes, f(n) is determined by {a_p} for all primes p.
    # The condition f(n) <= 1000 for n <= 1000 means:
    # \sum a_p v_p(n+1) <= 1000 for all n+1 <= 1001.
    # Since a_p >= 1, the maximum value of any a_p is when all other a_q are 1 (min possible).
    # e.g. a_3 * 6 + (count of other primes in x) * 1 <= 1000.
    # f(2024) = 4*a_3 + 2*a_5.
    # Possible values:
    # a_3 can be any integer from 1 to 166?
    # If a_3 = 166, then 6*166 = 996 <= 1000.
    # Then we need to check if a_5 can be something.
    # If x = 3^6 = 729, f(728) = 6*a_3 = 996 <= 1000.
    # If x = 3^4 * 5 = 81 * 5 = 405, f(404) = 4*a_3 + a_5 <= 1000.
    # If a_3=166, 4*166 + a_5 = 664 + a_5 <= 1000 => a_5 <= 336.
    # But a_5 also has its own constraint: 4*a_5 <= 1000 => a_5 <= 250.
    # So if a_3=166, a_5 can be 1..250.
    # In general, a_3 and a_5 just need to exist such that SOME a_p >= 1 satisfy the conditions.
    # The simplest condition is:
    # 1) 6*a_3 <= 1000 (from n+1 = 3^6 = 729)
    # 2) 4*a_5 <= 1000 (from n+1 = 5^4 = 625)
    # 3) 4*a_3 + 2*a_5 <= f(3^4 * 5^2 - 1) which is not constrained by n <= 1000.
    # Wait, 3^4 * 5 = 405 <= 1001. So 4*a_3 + a_5 <= 1000.
    # 3^2 * 5^2 = 9 * 25 = 225 <= 1001. So 2*a_3 + 2*a_5 <= 1000.
    # 3 * 5^3 = 3 * 125 = 375 <= 1001. So a_3 + 3*a_5 <= 1000.
    # These are the constraints on a_3 and a_5.
    # We want to know how many values 4*a_3 + 2*a_5 can take.
    pass

def count_f2024_values():
    values = set()
    # Constraints:
    # a3, a5 >= 1
    # 6*a3 <= 1000
    # 4*a5 <= 1000
    # 4*a3 + a5 <= 1000 (3^4 * 5 = 405)
    # 2*a3 + 2*a5 <= 1000 (3^2 * 5^2 = 225)
    # a3 + 3*a5 <= 1000 (3 * 5^3 = 375)
    # Are there others?
    # 3^5 * 2 = 243 * 2 = 486. So 5*a3 + a2 <= 1000. Since a2 >= 1, 5*a3 <= 999.
    # 5^2 * 2^5 = 25 * 32 = 800. So 2*a5 + 5*a2 <= 1000.
    # But a2 can be 1. So we just need to know if there EXISTS a_p >= 1.
    # The tightest constraints on (a3, a5) are those involving only a3, a5 and min a_p=1.
    # e.g. 3^4 * 5 * 2 = 810 <= 1001 => 4*a3 + a5 + a2 <= 1000. With a2=1, 4*a3 + a5 <= 999.
    # 3^2 * 5^2 * 2^2 = 900 <= 1001 => 2*a3 + 2*a5 + 2*a2 <= 1000. With a2=1, 2*a3 + 2*a5 <= 998.

    for a3 in range(1, 1001):
        if 6*a3 + 1 > 1000: break # 3^6 * 2 > 1001, but 3^6 = 729.
        # Actually 3^6 = 729 is the limit. So 6*a3 + (other primes) <= 1000.
        # Minimal other primes is none if n+1 is power of 3.
        # So 6*a3 <= 1000.
        for a5 in range(1, 1001):
            # Check all x = 3^i * 5^j * 2^k * ... <= 1001
            # We must have i*a3 + j*a5 + k*a2 + ... <= 1000
            # To see if a3, a5 is possible, we just need i*a3 + j*a5 + (sum of other v_p(x)) <= 1000
            # for all i, j such that 3^i * 5^j * (product of other primes) <= 1001.
            # The "worst" case is when we use the smallest other prime (2) as much as possible.
            possible = True
            for i in range(7): # 3^6 = 729
                for j in range(5): # 5^4 = 625
                    if i == 0 and j == 0: continue
                    rem = 1001 // (3**i * 5**j)
                    if rem == 0: continue
                    # Maximize k such that 3^i * 5^j * 2^k <= 1001
                    import math
                    k = int(math.log2(rem))
                    # sum of other exponents (primes > 5) is 0 for min f(n)
                    if i*a3 + j*a5 + k*1 > 1000:
                        possible = False; break
                if not possible: break

            if possible:
                values.add(4*a3 + 2*a5)

    print(f"Number of values f(2024) can take: {len(values)}")

if __name__ == "__main__":
    solve_alice_bob()
    count_f2024_values()

def solve_double_sum_floor():
    # f(n) = \sum_{j=1}^n j^1024 \lfloor 1/j + (n-i)/n \rfloor
    # Wait, the inner sum is over j, outer over i.
    # f(n) = \sum_{i=1}^n \sum_{j=1}^n j^1024 \lfloor 1/j + (n-i)/n \rfloor
    # Let k = n-i. i=1..n => k=0..n-1.
    # f(n) = \sum_{k=0}^{n-1} \sum_{j=1}^n j^1024 \lfloor 1/j + k/n \rfloor
    # \lfloor 1/j + k/n \rfloor:
    # If j=1: \lfloor 1 + k/n \rfloor = 1 for all k=0..n-1.
    # If j>1: 1/j + k/n < 1/2 + 1 = 1.5.
    # 1/j + k/n >= 1 ⟺ k/n >= 1 - 1/j ⟺ k >= n - n/j.
    # So for a fixed j > 1, the term j^1024 is included for k = \lceil n - n/j \rceil, ..., n-1.
    # Number of such k: n - \lceil n - n/j \rceil = \lfloor n/j \rfloor.
    # For j=1: 1^1024 is included for all n values of k. \lfloor n/1 \rfloor = n.
    # So f(n) = \sum_{j=1}^n j^1024 \lfloor n/j \rfloor.
    # N = f(M^15) - f(M^15 - 1)
    # f(m) - f(m-1) = \sum_{j=1}^m j^1024 \lfloor m/j \rfloor - \sum_{j=1}^{m-1} j^1024 \lfloor (m-1)/j \rfloor
    # \lfloor m/j \rfloor - \lfloor (m-1)/j \rfloor is 1 if j divides m, and 0 otherwise.
    # The j=m term in first sum is m^1024 * \lfloor m/m \rfloor = m^1024.
    # So f(m) - f(m-1) = \sum_{j|m, j<m} j^1024 + m^1024 = \sum_{j|m} j^1024.
    # Let \sigma_k(n) = \sum_{d|n} d^k. Then N = \sigma_1024(M^15).
    # M = 2 * 3 * 5 * 7 * 11 * 13.
    # M^15 = 2^15 * 3^15 * 5^15 * 7^15 * 11^15 * 13^15.
    # \sigma_1024(n) is multiplicative.
    # \sigma_1024(p^a) = \frac{p^{1024(a+1)} - 1}{p^{1024} - 1}.
    # N = \prod_{p \in {2,3,5,7,11,13}} \frac{p^{1024*16} - 1}{p^{1024} - 1}.
    # We want k such that 2^k || N.
    # v2(N) = \sum v2( \frac{p^{1024*16} - 1}{p^{1024} - 1} ).
    # For p=2: \frac{2^{1024*16} - 1}{2^{1024} - 1} is odd, so v2 = 0.
    # For odd p: v2( p^x - 1 ).
    # LTE Lemma: v2( p^x - 1 ) = v2(p-1) + v2(p+1) + v2(x) - 1 for even x.
    # Here x1 = 1024*16 = 2^14, x2 = 1024 = 2^10. Both even.
    # v2( \frac{p^{x1} - 1}{p^{x2} - 1} ) = v2(p^{x1} - 1) - v2(p^{x2} - 1)
    # = (v2(p-1) + v2(p+1) + 14 - 1) - (v2(p-1) + v2(p+1) + 10 - 1)
    # = 14 - 10 = 4.
    # This is for each odd p \in {3, 5, 7, 11, 13}.
    # There are 5 such primes. So k = 5 * 4 = 20.
    # We want 2^20 mod 5^7.
    # 5^7 = 78125.
    k = 20
    ans = pow(2, 20, 5**7)
    print(f"Problem 26de63 (Double sum) Solution: {ans}")

if __name__ == "__main__":
    solve_double_sum_floor()
