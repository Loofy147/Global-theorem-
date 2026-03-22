import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from core import extract_weights, verify_sigma, PRECOMPUTED, solve, run_equivariant_sa
from algebraic import get_algebraic_proof, parse_domain, export_lean_proof

class Engine:
    """
    The Global Structure Engine.
    """
    def __init__(self):
        pass

    def run(self, m: int, k: int, strategy: str = "standard") -> Dict[str, Any]:
        t0 = time.perf_counter()
        proof_obj = get_algebraic_proof(m, k)

        solution = None
        if proof_obj['exists'] == "PROVED_POSSIBLE":
            if (m, k) in PRECOMPUTED:
                solution = PRECOMPUTED[(m, k)]
            elif strategy == "equivariant":
                # Use a default Z2 orbit if none specified
                print(f"    Running equivariant SA for m={m}, k={k}...")
                solution, stats = run_equivariant_sa(m, [(m//2, m//2, m//2)] if m%2==0 else [(1,1,1)])
            else:
                solution = solve(m, k)

        verified = bool(solution and verify_sigma(solution, m))
        dt = time.perf_counter() - t0

        return {
            "m": m, "k": k, "status": proof_obj['exists'],
            "theorem": proof_obj['theorem'], "proof": proof_obj['proof'],
            "theorem_id": proof_obj.get("theorem_id"),
            "theorem_name": proof_obj.get("theorem_name"),
            "witness_hash": proof_obj['witness_hash'],
            "solution_found": verified, "elapsed_ms": dt * 1000
        }

    def analyse_text(self, desc: str, strategy: str = "standard") -> Dict[str, Any]:
        """Automatically parses description and classifies."""
        d = parse_domain(desc)
        res = self.run(d['m'], d['k'], strategy=strategy)
        res['parsed'] = d
        return res

if __name__ == "__main__":
    import sys
    e = Engine()

    if "--parse" in sys.argv:
        idx = sys.argv.index("--parse")
        desc = " ".join(sys.argv[idx+1:])
        strat = "equivariant" if "--equivariant" in sys.argv else "standard"
        res = e.analyse_text(desc, strategy=strat)
        print(f"\n--- Analysis for Domain: {res['parsed']['G']} ---")
        print(f"SES: {res['parsed']['SES']}")
        if res.get('theorem_id'):
            print(f"Applies Theorem {res['theorem_id']}: {res['theorem_name']}")
        print(f"Status: {res['status']}")
        print(f"Proof Steps:")
        for line in res['proof']: print(f"  {line}")
        print(f"Classification Time: {res['elapsed_ms']:.2f}ms")
        if res['solution_found']:
            print(f"Solution: Found and Verified ✓")

    elif "--lean" in sys.argv:
        m, k = int(sys.argv[2]), int(sys.argv[3])
        print(export_lean_proof(m, k))

    else:
        # Default batch run
        for m, k in [(3,3), (4,3), (4,4), (6,3)]:
            res = e.run(m, k)
            print(f"G_{m}(k={k}): {res['status']} ({res['elapsed_ms']:.2f}ms)")
