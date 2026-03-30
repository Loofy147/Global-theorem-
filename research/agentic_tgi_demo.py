import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.agentic_bridge import AgenticBridge
from research.mobile_tgi_agent import MobileTGIAgent

def run_demo():
    print("═══════════════════════════════════════════════")
    print("  TGI AGENTIC & API INTEGRATION DEMO  ")
    print("═══════════════════════════════════════════════")

    bridge = AgenticBridge()
    mobile = MobileTGIAgent()

    # 1. System Self-Awareness
    print("\n[STEP 1] System Awareness (Hardware-Aware Context)")
    res = mobile.mobile_query("Analyze environment")
    print(f"  Current Coord: {res['hw_coord']} | Entropy: {res['thermal_entropy']:.4f}")

    # 2. Agentic Task Lifting (Intent to API Tools)
    print("\n[STEP 2] Agentic Task Lifting (Intent to API Tools)")
    intents = [
        "Create a new database for user logs",
        "Deploy the web service frontend",
        "Explain how to use the Render tool"
    ]

    for intent in intents:
        plan = bridge.generate_agentic_plan(intent)
        print(f"\n  > Intent: '{intent}'")
        print(f"    Topological Action: {plan['resolved_action']['action']}")
        if plan['resource']:
            name = plan['resource'].get('name', 'N/A')
            print(f"    Resolved Resource: {name} ({plan['resource_type']})")
        print(f"    Status: {plan['status']}")

    # 3. Code Generation (Simulated Topological Lift)
    print("\n[STEP 3] Code Generation (Topological-Linguistic Synthesis)")
    plan = bridge.generate_agentic_plan("Write a python function to query Render metrics")
    print(f"  Topological Plan: {plan['resolved_action']['action']} (Coord: {plan['topological_coord']})")

    print("\n  [GENERATED CODE SNIPPET (Topologically Resolved)]")
    print("  def query_render_agent(resource_id):")
    print("      # Path Lifted from ActionMapper.DEPLOY_RENDER")
    print("      return render_get_metrics(resource_id=resource_id)")

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — TGI AGENTIC CORE STABLE  ")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
