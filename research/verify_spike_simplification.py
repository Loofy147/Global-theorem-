import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma

def verify_simplification(m):
    sig = construct_spike_sigma(m)
    if not sig: return False

    # Extract table[s][j]
    table = [{} for _ in range(m)]
    for (i,j,k), p in sig.items():
        s = (i+j+k)%m
        table[s][j] = p

    for s in range(m):
        p0 = table[s][0]
        for j in range(m - 1):
            if table[s][j] != p0:
                print(f"  m={m}, s={s}: j={j} differs from j=0")
                return False
    return True

if __name__ == "__main__":
    for m in [3, 5, 7, 9, 11]:
        res = verify_simplification(m)
        print(f"m={m}: {'Simplified' if res else 'Complex'}")
