import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.tgi_agent import TGIAgent
from research.agentic_bridge import AgenticBridge
from research.agentic_action_engine import TopologicalActionEngine

def run_demo():
    agent = TGIAgent()
    bridge = AgenticBridge()
    engine = TopologicalActionEngine()

    print("═══════════════════════════════════════════════")
    print("  TGI AGENTIC EXPANSION DEMO — March 2026  ")
    print("═══════════════════════════════════════════════")

    print("\n[1] Verifying Expanded Ontology State...")
    print(agent.ontology_summary())

    print("\n[2] Agentic Intent Resolution (Topological-to-Tool Mapping)")
    intent = "Deploy a web service on Render with auto-deploy"
    print(f"  Intent: '{intent}'")
    plan = bridge.generate_agentic_plan(intent)
    # Since generate_agentic_plan returns a list now
    step1 = plan[0]
    print(f"    - Manifold: {step1['manifold']}")
    print(f"    - Action: {step1['action']}")
    print(f"    - Resource: {step1['resource']} ({step1['type']})")

    print("\n[3] Multi-Modal Path Lifting (Cross-Domain Intent)")
    intents = [
        "Query student grades from Supabase",
        "Generate a RAG response for the user",
        "Analyze high-res medical imagery",
        "Ingest a new dataset into the TGI ontology"
    ]
    for it in intents:
        p = bridge.generate_agentic_plan(it)[0]
        print(f"  - Intent: '{it[:30]}...' -> Tool: {p['resource']} on {p['manifold']}")

    print("\n[4] Full Autonomous Execution Loop (Feedback Re-Ingestion)")
    # We'll use the autonomous query flow
    res = agent.autonomous_query("Solve x^2 - 4 = 0 and notify me")
    print(f"  Autonomous Manifold: {res['manifold']}")
    print(f"  Generated Path Steps: {res['path_length']}")

    plan = res['plan']
    print(f"  Executing Plan ({len(plan)} steps):")
    results = engine.executor.execute_plan(plan)
    for r in results:
        print(f"    Step {r['step']}: {r['action']} -> {r['result']['status']}")

    print("\n[5] Verifying Loop Closure (Self-Reflection)")
    print(f"  New Log Entries in Ontology: {len([e for e in agent.core.ontology.grid.values() if 'LOG_' in e['name']])}")

    print("\n═══ TGI AGENTIC EXPANSION COMPLETE ═══")

if __name__ == "__main__":
    run_demo()
