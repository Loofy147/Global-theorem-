from core import run_hybrid_sa, repair_manifold, verify_sigma, _sa_score, _build_sa
import random

m, k = 3, 3
n, arc_s, pa, all_p = _build_sa(m, k)
nP = len(all_p)

from core import PRECOMPUTED
target = PRECOMPUTED[(3,3)]
sigma_list = []
for i in range(m):
    for j in range(m):
        for k_ in range(m):
            sigma_list.append(all_p.index(list(target[(i,j,k_)])))

for pi in range(nP):
    sigma_list[0] = pi
    ns = _sa_score(sigma_list, arc_s, pa, n, k)
    print(f"Perm {pi}: Score {ns}")
