import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma, verify_sigma

m = 3
sol = construct_spike_sigma(m, 3)
if sol:
    print(f"m={m} found a solution.")
    print("Verification:", verify_sigma(sol, m))
else:
    print(f"m={m} NO solution found.")
