import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma, verify_sigma

m = 3
sig = construct_spike_sigma(m)
print(f"m={m} verified: {verify_sigma(sig, m)}")

# Print table[s][j]
# sigma[(i,j,k)] = table[s][j] where s = (i+j+k)%m
# Let's extract table back
table = [{} for _ in range(m)]
for i, j, k in sig:
    s = (i+j+k)%m
    table[s][j] = sig[(i,j,k)]

for s in range(m):
    print(f"s={s}:")
    for j in range(m):
        print(f"  j={j}: {table[s][j]}")
