import subprocess
import json
import re

def get_stats(kernel_id):
    try:
        # Download output
        subprocess.run(["kaggle", "kernels", "output", kernel_id, "-p", "tmp_res"], check=True, capture_output=True)
        # Find log file
        log_file = None
        import os
        for f in os.listdir("tmp_res"):
            if f.endswith(".log"):
                log_file = os.path.join("tmp_res", f)
                break
        if not log_file: return None

        with open(log_file, "r") as f:
            content = f.read()
            # Search for Final Stats: {'best': 2, ...}
            match = re.search(r"Final Stats: ({.*?})", content)
            if match:
                return eval(match.group(1))
    except:
        pass
    finally:
        import shutil
        if os.path.exists("tmp_res"):
            shutil.rmtree("tmp_res")
    return None

def main():
    username = "hichambedrani"
    # Get all kernels
    res = subprocess.check_output(["kaggle", "kernels", "list", "--user", username, "--sort-by", "dateRun"], text=True)
    lines = res.split('\n')[2:]

    results = {}
    for line in lines:
        if not line.strip(): continue
        parts = line.split()
        kernel_id = parts[0]
        if "massive" in kernel_id or "-v3" in kernel_id:
            print(f"Checking {kernel_id}...")
            stats = get_stats(kernel_id)
            if stats:
                results[kernel_id] = stats
                print(f"  Result: {stats}")

    with open("research/swarm_final_stats.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
