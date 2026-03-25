import json
import sys
import os
import ast

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import verify_sigma

def verify():
    try:
        with open("research/p1_solution/solution.json", "r") as f:
            content = f.read()
            # Kernel might have printed it as a python dict string
            try:
                sol_raw = json.loads(content)
            except:
                sol_raw = ast.literal_eval(content)

        sol = {}
        for k, v in sol_raw.items():
            if isinstance(k, str):
                k = eval(k)
            sol[k] = tuple(v)

        print(f"Loaded solution with {len(sol)} vertices.")
        valid = verify_sigma(sol, 4)
        print(f"VERIFICATION: {'PASSED' if valid else 'FAILED'}")

        if valid:
            # Save a compressed version for core.py
            with open("research/p1_solution_verified.json", "w") as f:
                json.dump(sol_raw, f)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
