import sys, os
import subprocess

def run_cmd(cmd):
    print(f"Running: {cmd}")
    env = os.environ.copy()
    env["PYTHONPATH"] = f".:{env.get('PYTHONPATH', '')}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    if res.returncode != 0:
        print(f"FAILED: {cmd}")
        print(res.stderr)
        return False
    print(res.stdout)
    return True

if __name__ == "__main__":
    checks = [
        "python3 research/verify_deterministic_spike.py",
        "python3 research/fso_fabric.py",
        "python3 research/fso_mesh_daemon.py",
        "python3 research/fso_production_search.py",
        "python3 research/fso_distributed_intel_app.py",
        "python3 research/fso_holographic_demo.py"
    ]
    all_ok = True
    for check in checks:
        if not run_cmd(check):
            all_ok = False

    if not all_ok:
        sys.exit(1)
    print("ALL CHECKS PASSED")
