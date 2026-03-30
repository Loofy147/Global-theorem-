import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.agentic_bridge import AgenticBridge

def run_demo():
    print("═══════════════════════════════════════════════")
    print("  TGI LIBRARY-AWARE AGENTIC DEMO  ")
    print("═══════════════════════════════════════════════")

    bridge = AgenticBridge()

    intents = [
        "Compute the Hamiltonian cycle using linear algebra",
        "Build a touch-enabled Android UI",
        "Monitor system CPU and RAM utilization",
        "Solve a symbolic equation for G_m^k"
    ]

    for intent in intents:
        plan = bridge.generate_agentic_plan(intent)
        print(f"\n  > Intent: '{intent}'")
        print(f"    Action: {plan['resolved_action']['action']} (Coord: {plan['topological_coord']})")
        if plan['resource']:
            print(f"    Resource: {plan['resource'].get('name', 'N/A')} [{plan['resource_type']}]")
            print(f"    Domain: {plan['resource'].get('domain', 'N/A')}")
        print(f"    Status: {plan['status']}")

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — LIBRARY-AWARE CORE STABLE  ")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
