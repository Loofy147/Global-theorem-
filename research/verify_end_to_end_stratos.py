import asyncio
import aiohttp
import sys
import os
import time
import json
import subprocess
import signal

# Add the stratos-os directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'stratos-os')))

async def run_verification():
    print("=== STRATOS E2E: LOCAL NODE + CLIENT VERIFICATION ===")

    # 1. Start the Global Node locally on port 10001
    env = os.environ.copy()
    env["PORT"] = "10001"
    env["PYTHONPATH"] = f".:{env.get('PYTHONPATH', '')}"

    node_proc = subprocess.Popen(
        [sys.executable, "research/fso_global_node.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("[*] Starting local FSO Node on port 10001...")

    # Wait for node to be ready
    max_retries = 30
    ready = False
    for i in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:10001/health", timeout=1) as resp:
                    if resp.status == 200:
                        ready = True
                        break
        except Exception as e:
            pass

        # Check if process is still running
        if node_proc.poll() is not None:
            stdout, stderr = node_proc.communicate()
            print(f"[!] Node crashed with code {node_proc.returncode}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False

        print(f"[*] Waiting for node... ({i+1}/{max_retries})")
        time.sleep(1)

    if not ready:
        print("[!] Node failed to start or respond.")
        node_proc.kill()
        return False

    print("[+] Local FSO Node is ready.")

    try:
        # 2. Inject some dummy logic into the node's local manifest file for the test
        manifest_path = "research/fso_production_manifest.json"
        original_manifest = {}
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r") as f:
                    original_manifest = json.load(f)
            except: pass

        test_logic = {
            "test_lib.greet": "def greet(name): return f'Hello from Torus, {name}!'"
        }

        with open(manifest_path, "w") as f:
            json.dump(test_logic, f)

        print("[*] Injected test logic into local manifest.")

        # 3. Use stratos-os to import the logic
        from stratos.engine import StratosCloudEngine
        import stratos

        # Point the client to the local node
        stratos._MANIFOLD = StratosCloudEngine(genesis_ip="localhost:10001")

        print("\n[*] Attempting topological import: 'import stratos.test_lib'...")
        # Clear module from cache if it exists from previous runs
        if 'stratos.test_lib' in sys.modules:
            del sys.modules['stratos.test_lib']

        import stratos.test_lib as t_lib

        print(f"[+] Import successful! Module: {t_lib}")

        result = t_lib.greet("Jules")
        print(f"[+] Execution Test: t_lib.greet('Jules') -> {result}")

        if result == "Hello from Torus, Jules!":
            print("\n[SUCCESS] End-to-End Verification Complete.")
            success = True
        else:
            print(f"\n[FAILURE] Unexpected result: {result}")
            success = False

    except Exception as e:
        print(f"[!] Verification Failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    finally:
        # Restore manifest
        with open(manifest_path, "w") as f:
            json.dump(original_manifest, f)

        # Kill node process
        print("[*] Shutting down FSO Node...")
        os.kill(node_proc.pid, signal.SIGTERM)
        node_proc.wait()

    return success

if __name__ == "__main__":
    success = asyncio.run(run_verification())
    sys.exit(0 if success else 1)
