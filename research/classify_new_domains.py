from algebraic import parse_domain, analyze_advanced_domain

domains = ["icosahedral", "crystal", "diamond", "hamming"]
for d in domains:
    print(f"\n--- Domain: {d} ---")
    res = analyze_advanced_domain(d)
    print(res)

print("\n--- AIMO Functional Equation Pattern ---")
from research.aimo_p7_solver import count_f2024_values
vals = count_f2024_values()
print(f"Number of values for f(2024): {len(vals)}")
