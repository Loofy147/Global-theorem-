import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tgi_agent import TGIAgent
from tgi_core import TGICore

def run_demo():
    print("═══════════════════════════════════════════════")
    print("  TGI SYSTEM DEMO — Full Pipeline Integration  ")
    print("═══════════════════════════════════════════════")

    agent = TGIAgent()

    # Domain 1: Language (m=25, k=3)
    print("\n--- Domain 1: Natural Language ---")
    response = agent.query("Topology is the study of")
    print(response)

    # Domain 2: Math (m=9, k=3)
    print("\n--- Domain 2: Symbolic Reasoning ---")
    response = agent.query("x + 5 = 14")
    print(response)

    # Domain 3: Binary / Algebraic (m=2, k=4)
    print("\n--- Domain 3: Error Correction / Binary ---")
    response = agent.query("1010111")
    print(response)

    # Domain 4: Reflection on Obstruction (m=4, k=3)
    print("\n--- Domain 4: Topological Reflection ---")
    core = TGICore(4, 3)
    print(f"Reflecting on Obstruction: {core.reflect()}")

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — System Integration Successful")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
