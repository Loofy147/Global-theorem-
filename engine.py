import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from core import extract_weights, verify_sigma, PRECOMPUTED, solve
from algebraic import get_algebraic_proof

class Engine:
    """
    The Global Structure Engine.

    Given a symmetric combinatorial problem (m, k), it classifies it
    in under a second and provides a machine-verifiable proof.
    """
    def __init__(self):
        pass

    def run(self, m: int, k: int) -> Dict[str, Any]:
        t0 = time.perf_counter()

        # 1. Algebraic Classification
        proof_obj = get_algebraic_proof(m, k)

        # 2. Construction Route
        solution = None
        if proof_obj['exists'] == "PROVED_POSSIBLE":
            if (m, k) in PRECOMPUTED:
                solution = PRECOMPUTED[(m, k)]
            else:
                solution = solve(m, k)

        verified = bool(solution and verify_sigma(solution, m))

        dt = time.perf_counter() - t0
        return {
            "m": m,
            "k": k,
            "status": proof_obj['exists'],
            "theorem": proof_obj['theorem'],
            "proof": proof_obj['proof'],
            "witness_hash": proof_obj['witness_hash'],
            "solution_found": verified,
            "elapsed_ms": dt * 1000
        }

if __name__ == "__main__":
    import sys
    e = Engine()
    if len(sys.argv) > 2:
        m, k = int(sys.argv[1]), int(sys.argv[2])
        res = e.run(m, k)
        print(f"\n--- G_{m} (k={k}) ---")
        print(f"Status: {res['status']}")
        print(f"Theorem: {res['theorem']}")
        for line in res['proof']: print(f"  {line}")
        print(f"Solution Found/Verified: {res['solution_found']}")
        print(f"Witness Hash: {res['witness_hash']}")
        print(f"Total Time: {res['elapsed_ms']:.2f}ms")
    else:
        for m, k in [(4,3), (4,4), (6,3), (5,3)]:
            res = e.run(m, k)
            print(f"G_{m}(k={k}): {res['status']} ({res['elapsed_ms']:.2f}ms)")
