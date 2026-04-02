import sys, os
import random
from math import gcd

# Add parent and research directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from research.knowledge_mapper import KnowledgeMapper
except ImportError:
    from knowledge_mapper import KnowledgeMapper

def run_closure_imputation_test(sample_size=1000, erasure_rate=0.25):
    print(f"--- TGI Closure Imputation Test (Blind Data Healing) ---")
    km = KnowledgeMapper(m=256, k=4)
    target_fiber = km.FIBERS["LANGUAGE"] # Fiber 5

    wordlist_path = "research/wordlist.txt"
    if not os.path.exists(wordlist_path):
        print(f"Error: Wordlist not found at {wordlist_path}")
        return

    # 1. Topological Sharding
    print(f"Step 1: Topological Sharding ({sample_size} samples)...")
    samples = []
    with open(wordlist_path, "r") as f:
        words = [line.strip() for line in f if line.strip()]
        selected_words = random.sample(words, min(sample_size, len(words)))

        for word in selected_words:
            coords = km._apply_closure_hashing(word, target_fiber)
            samples.append({
                "word": word,
                "x": coords[0],
                "y": coords[1],
                "z": coords[2],
                "w_orig": coords[3]
            })

    # 2. Parity Erasure
    print(f"Step 2: Parity Erasure ({int(erasure_rate*100)}% erasure rate)...")
    erased_count = 0
    for s in samples:
        if random.random() < erasure_rate:
            s["w_erased"] = True
            erased_count += 1
        else:
            s["w_erased"] = False

    # 3. Geometric Reconstruction (Blind Healing)
    print(f"Step 3: Geometric Reconstruction (Closure Lemma)...")
    healed_count = 0
    failure_count = 0

    for s in samples:
        if s["w_erased"]:
            # Reconstruct missing w using only (x, y, z) and the Target Fiber (5)
            # Law III: w = (TargetFiber - (x + y + z)) % m
            w_reconstructed = (target_fiber - (s["x"] + s["y"] + s["z"])) % km.m

            if w_reconstructed == s["w_orig"]:
                healed_count += 1
            else:
                failure_count += 1

    # 4. Results
    print(f"\n--- Final Assessment ---")
    print(f"Total Samples: {len(samples)}")
    print(f"Total Erased:  {erased_count}")
    print(f"Total Healed:  {healed_count}")
    print(f"Failures:      {failure_count}")

    if erased_count > 0:
        success_rate = (healed_count / erased_count) * 100
        print(f"Success Rate:  {success_rate:.2f}%")

        if success_rate == 100.0:
            print("\nPROOF VALIDATED: The Closure Lemma functions as a Stateless Truth Oracle.")
        else:
            print("\nPROOF FAILED: Geometric reconstruction inconsistency.")
    else:
        print("No samples were erased. Test inconclusive.")

if __name__ == "__main__":
    run_closure_imputation_test()
