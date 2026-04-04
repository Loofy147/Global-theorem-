import sys, os
import polars as pl
import pandas as pd
import numpy as np

# Ensure research modules are accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the kaggle_evaluation if not present (for local testing)
try:
    import kaggle_evaluation.aimo_3_inference_server as isrv
except ImportError:
    print("[!] Kaggle Inference Server not found. Mocking for local development.")
    class MockServer:
        def __init__(self, predict_fn):
            self.predict_fn = predict_fn
        def serve(self):
            print("[MOCK] Server is now listening for requests.")
        def run_local_gateway(self, data_paths=None):
            print("[MOCK] Running local gateway with paths:", data_paths)
            # Simulate a few problems
            mock_test = pl.DataFrame({
                "id": ["0e644e", "9c1c5f", "999zzz"],
                "problem": [
                    "Reference problem (0e644e)",
                    "Functional equation f(m) + f(n) = f(m + n + mn)...",
                    "A new, unsolved math challenge."
                ]
            })
            for row in mock_test.iter_slices(n_rows=1):
                res = self.predict_fn(row, None)
                print(f"[PREDICTION] Problem {row.get_column('id')[0]}: {res.get_column('answer')[0]}")

    class isrv:
        AIMO3InferenceServer = MockServer

from research.tgi_aimo_solver import TGIAIMOSolver

# Initialize the TGI Solver
solver = TGIAIMOSolver()

def predict(problem_row, sample_submission):
    """
    Main prediction loop for AIMO Progress Prize 3.
    Processes rows using the TGI-AIMO Reasoning Engine.
    """
    try:
        # Handle both Polars Series and DataFrame inputs from Synchronous API
        if hasattr(problem_row, 'get_column'):
            problem_id = str(problem_row.get_column('id')[0])
            problem_text = str(problem_row.get_column('problem')[0])
        else:
            # Fallback for older API versions or simple list inputs
            problem_id = str(problem_row[0])
            problem_text = str(problem_row[1]) if len(problem_row) > 1 else ""

        # Solve via TGI Manifold + Healing Lemma
        ans = solver.solve_problem(problem_text, problem_id)

        # Ensure result is an integer mod 100,000 as per competition rules
        ans = int(ans) % 100000

        # Return a compliant Polars DataFrame
        return pl.DataFrame({'id': [problem_id], 'answer': [ans]})

    except Exception as e:
        print(f"[!] Inference Error: {e}")
        # Robust fallback: return 0 if everything fails
        try:
            p_id = problem_id if 'problem_id' in locals() else 'error'
            return pl.DataFrame({'id': [p_id], 'answer': [0]})
        except:
            return pl.DataFrame({'id': ['err'], 'answer': [0]})

def run():
    """Starts the Kaggle AIMO Inference Server."""
    server = isrv.AIMO3InferenceServer(predict)

    if os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
        print("[*] Production Rerun Mode: Serve() activated.")
        server.serve()
    else:
        # Local gateway testing using mock or provided test data
        import glob
        test_files = glob.glob('/kaggle/input/**/test.csv', recursive=True)
        if test_files:
            print(f"[*] Found local test data: {test_files[0]}")
            server.run_local_gateway(data_paths=(test_files[0],))
        else:
            print("[*] No test data found. Running mock evaluation.")
            server.run_local_gateway()

if __name__ == "__main__":
    run()

def generate_offline_parquet(test_df: pl.DataFrame, output_path: str = "submission.parquet"):
    """Generates a submission.parquet file for offline evaluation."""
    print(f"[*] Offline mode: Generating {output_path} from input data...")
    predictions = []
    for row in test_df.iter_slices(n_rows=1):
        pred_df = predict(row, None)
        predictions.append(pred_df)

    final_df = pl.concat(predictions)
    final_df.write_parquet(output_path)
    print(f"[+] Saved {len(final_df)} predictions to {output_path}.")

# Check if we should run in offline generator mode
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Generate submission.parquet offline")
    args, unknown = parser.parse_known_args()

    if args.offline:
        mock_data = pl.DataFrame({
            "id": ["p1", "p2", "p3"],
            "problem": ["What is 2+2?", "remainder when 3^5 is divided by 10", "Complex healing problem."]
        })
        generate_offline_parquet(mock_data)
