import sys
import os
import unittest.mock
from unittest.mock import MagicMock

# Add the stratos-os directory to sys.path to simulate it being installed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'stratos-os')))

def test_infinite_import():
    print("=== STRATOS PYPI: INFINITE IMPORT VERIFICATION ===")

    # 1. Mock the StratosCloudEngine to return a logic bundle
    mock_logic = {
        "vllm.run_inference": "def run_inference(prompt): return f'Topological Inference: {prompt}'",
        "vllm.Version": "VERSION = '1.0.0-Torus'"
    }

    # We need to mock the instance of StratosCloudEngine that is initialized in stratos/__init__.py
    with unittest.mock.patch('stratos._MANIFOLD') as mock_manifold:
        mock_manifold.fetch_and_unbind.return_value = mock_logic

        print("\n[*] Attempting topological import: 'import stratos.vllm'...")
        try:
            import stratos.vllm as vllm

            print(f"[+] Import successful! Module: {vllm}")

            # Verify the functions and variables are present in the module
            if hasattr(vllm, 'run_inference'):
                result = vllm.run_inference("Hello FSO")
                print(f"[+] Execution Test: vllm.run_inference('Hello FSO') -> {result}")
            else:
                print("[!] Error: run_inference not found in vllm module")
                return False

            if hasattr(vllm, 'VERSION'):
                print(f"[+] Metadata Test: vllm.VERSION -> {vllm.VERSION}")
            else:
                print("[!] Error: VERSION not found in vllm module")
                return False

            print("\n[SUCCESS] Infinite Import verified. Logic reconstituted in RAM.")
            return True

        except Exception as e:
            print(f"[!] Verification Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_infinite_import()
    sys.exit(0 if success else 1)
