import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma

def extract(m):
    sig = construct_spike_sigma(m)
    # sigma[(i,j,k)] = table[s][j]
    table = [{} for _ in range(m)]
    for (i,j,k), p in sig.items():
        s = (i+j+k)%m
        table[s][j] = p

    # Analyze table
    print(f"--- m={m} Analysis ---")
    for s in range(m):
        # All j < m-1 should have same p
        p_base = table[s][0]
        p_spike = table[s][m-1]
        print(f"  s={s}: j<m-1 -> {p_base}, j=m-1 -> {p_spike}")

extract(3)
extract(5)
