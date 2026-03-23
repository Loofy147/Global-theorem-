import time, sys
from typing import Dict, List, Optional, Tuple, Any, Callable
from core import extract_weights, verify_sigma, PRECOMPUTED, solve, run_hybrid_sa
from algebraic import get_algebraic_proof, parse_domain, export_lean_proof

class Domain:
    def __init__(self, name, n, k, m, fiber_map, tags, precomputed=None, group="", notes=""):
        self.name=name; self.n=n; self.k=k; self.m=m; self.fiber_map=fiber_map
        self.tags=tags; self.precomputed=precomputed; self.group=group; self.notes=notes


class Engine:
    """
    The Global Structure Engine provides a unified interface for classifying
    and solving combinatorial problems using the Short Exact Sequence framework.
    """
    def register(self, domain: Domain):
        self.registry.append(domain)

    def print_results(self):
        print(f'\n--- Engine Registry: {len(self.registry)} Domains ---')
        for d in self.registry:
            print(f'  {d.name:<40} (n={d.n}, k={d.k}, m={d.m})')

    def __init__(self):
        self.registry = []
        """Initializes the discovery engine."""
        pass

    def run(self, m: int, k: int, strategy: str = "standard") -> Dict[str, Any]:
        """
        Runs the classification and optional search for a problem (m, k).

        Args:
            m: The group order (Z_m).
            k: The dimension (number of cycles).
            strategy: Search strategy ('standard', 'hybrid', 'equivariant').

        Returns:
            A dictionary containing the status, proof steps, and solution if found.
        """
        t0 = time.perf_counter()
        proof_obj = get_algebraic_proof(m, k)

        solution = None
        if proof_obj['exists'] == "PROVED_POSSIBLE":
            if (m, k) in PRECOMPUTED:
                solution = PRECOMPUTED[(m, k)]
            elif strategy == "hybrid":
                print(f"    Running hybrid SA for m={m}, k={k}...")
                solution, stats = run_hybrid_sa(m, k=k)
            else:
                solution = solve(m, k)

        verified = bool(solution and verify_sigma(solution, m))
        dt = time.perf_counter() - t0

        return {
            "m": m, "k": k, "status": proof_obj['exists'],
            "theorem": proof_obj.get('theorem', ''),
            "proof": proof_obj.get('proof', []),
            "theorem_id": proof_obj.get("theorem_id"),
            "theorem_name": proof_obj.get("theorem_name"),
            "witness_hash": proof_obj.get('witness_hash', ''),
            "solution_found": verified, "elapsed_ms": dt * 1000
        }

    def analyse_text(self, desc: str, strategy: str = "standard") -> Dict[str, Any]:
        """
        Automatically parses a text description and classifies the domain.

        Args:
            desc: Text description of the problem.
            strategy: Search strategy to use.
        """
        d = parse_domain(desc)
        res = self.run(d['m'], d['k'], strategy=strategy)
        res['parsed'] = d
        return res

    def simplify_problem(self, m: int, k: int) -> Dict[str, Any]:
        """
        Uses categorical morphisms (Quotient, Product) to reduce a complex problem
        to smaller solvable components.
        """
        suggested = get_suggested_morphisms(m, k)
        reduction = None
        for m_ in suggested:
            if m_.kind == "Quotient":
                # Check if quotient is solvable
                sub_res = self.run(int(m_.target.split('_')[-1]), k)
                if sub_res['status'] == "PROVED_POSSIBLE":
                    reduction = {
                        "kind": m_.kind,
                        "source": m_.source,
                        "target": m_.target,
                        "status": "REDUCIBLE",
                        "proof": f"Reduces to solvable quotient {m_.target}."
                    }
                    break
        return reduction or {"status": "IRREDUCIBLE"}

    def get_lean_export(self, m: int, k: int) -> str:
        """Generates Lean 4 source for the parity obstruction proof."""
        return export_lean_proof(m, k)

def get_suggested_morphisms(m: int, k: int) -> List[Any]:
    """Suggests ways to simplify or solve (m, k) using known components."""
    class Morphism:
        def __init__(self, kind: str, source: str, target: str):
            self.kind = kind; self.source = source; self.target = target
    m_list = []
    for q in range(2, m):
        if m % q == 0:
            m_list.append(Morphism("Lift", f"G_{q}", f"G_{m}"))
            m_list.append(Morphism("Quotient", f"G_{m}", f"G_{q}"))
    factors = [i for i in range(2, m) if m % i == 0]
    for f in factors:
        other = m // f
        if other > 1:
            m_list.append(Morphism("Product", f"G_{f} x G_{other}", f"G_{m}"))
    return m_list

def check_remote_search_status() -> Dict[str, str]:
    """Checks the status of Kaggle search kernels if CLI is configured."""
    import subprocess
    kernels = [
        "hichambedrani/claudes-cycles-p1-equiv",
        "hichambedrani/claudes-cycles-p2-equiv"
    ]
    status = {}
    for k in kernels:
        try:
            res = subprocess.check_output(["kaggle", "kernels", "status", k],
                                          stderr=subprocess.STDOUT, text=True)
            status[k.split('/')[-1]] = res.strip()
        except:
            status[k.split('/')[-1]] = "Unknown (API not configured?)"
    return status

if __name__ == "__main__":
    e = Engine()

    if "--remote" in sys.argv:
        stats = check_remote_search_status()
        print("\n--- Remote Kaggle Search Status ---")
        for k, v in stats.items():
            print(f"  {k}: {v}")

    elif "--parse" in sys.argv:
        idx = sys.argv.index("--parse")
        desc = " ".join(sys.argv[idx+1:])
        strat = "hybrid" if "--hybrid" in sys.argv else "standard"
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
        idx = sys.argv.index("--lean")
        m, k = int(sys.argv[idx+1]), int(sys.argv[idx+2])
        print(e.get_lean_export(m, k))

    elif "--morphisms" in sys.argv:
        m, k = int(sys.argv[sys.argv.index("--morphisms")+1]), int(sys.argv[sys.argv.index("--morphisms")+2])
        morphs = get_suggested_morphisms(m, k)
        print(f"\n--- Suggested Morphisms for G_{m} (k={k}) ---")
        for morph in morphs:
            print(f"  {morph.kind:10} : {morph.source:15} -> {morph.target}")

    else:
        for m, k in [(3,3), (4,3), (4,4), (6,3)]:
            res = e.run(m, k)
            print(f"G_{m}(k={k}): {res['status']} ({res['elapsed_ms']:.2f}ms)")
