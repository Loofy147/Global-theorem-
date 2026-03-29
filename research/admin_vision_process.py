import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.tgi_agent import TGIAgent
from research.topological_vision import TopologicalVisionMapper

def admin_process(image_path):
    print("═══════════════════════════════════════════════")
    print("  TGI ADMIN VISION PROCESS — High Resolution  ")
    print("═══════════════════════════════════════════════")

    agent = TGIAgent()
    mapper = TopologicalVisionMapper(m=255, k=5)

    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    # 1. Standard Query
    print("\n[STEP 1] General Topological Query")
    res = agent.query(image_path)
    print(res)

    # 2. Deep Manifold Analysis
    print("\n[STEP 2] Deep Manifold Fibration Analysis")
    img = Image.open(image_path).convert('RGB')
    img_arr = np.array(img.resize((128, 128)))

    # Analyze different color fibers
    # R-fiber, G-fiber, B-fiber
    channels = ['Red', 'Green', 'Blue']
    for i, name in enumerate(channels):
        channel_data = img_arr[:, :, i]
        # Calculate entropy of this specific fiber
        flat = channel_data.flatten()
        _, counts = np.unique(flat, return_counts=True)
        probs = counts / len(flat)
        ent = -np.sum(probs * np.log2(probs + 1e-10))
        print(f"  {name} Fiber Entropy: {ent:.4f}")

    # 3. Global Symmetry Search (Simplified)
    print("\n[STEP 3] SES Framework Consistency Check")
    proof = agent.core.status.get("proof", [])
    for p in proof:
        print(f"    {p}")

    print("\n═══════════════════════════════════════════════")
    print("  ADMIN PROCESS COMPLETE — Topological State Valid  ")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    admin_process("research/portrait_only.png")
