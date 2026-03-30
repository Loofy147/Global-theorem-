import random
from core import verify_sigma, table_to_sigma
from itertools import permutations

all_p = list(permutations(range(3)))
rng = random.Random(42)
for att in range(100000):
    table = []
    for s in range(3):
        row = {j: rng.choice(all_p) for j in range(3)}
        table.append(row)
    sigma = table_to_sigma(table, 3)
    if verify_sigma(sigma, 3):
        print(f"Found m=3 at attempt {att}")
        # Convert to list of lists for representation
        print([[table[s][j] for j in range(3)] for s in range(3)])
        break
