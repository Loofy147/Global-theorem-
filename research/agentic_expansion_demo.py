import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.agentic_bridge import AgenticBridge
from research.tgi_agent import TGIAgent

def run_demo():
    print("═══════════════════════════════════════════════")
    print("  TGI AGENTIC EXPANSION DEMO — March 2026  ")
    print("═══════════════════════════════════════════════")

    bridge = AgenticBridge()
    agent = TGIAgent()

    # 1. Ontology State Verification
    print("\n[1] Verifying Expanded Ontology State...")
    print(agent.ontology_summary())

    # 2. Agentic Intent Resolution (Cloud/DB/Docs/AI)
    print("\n[2] Agentic Intent Resolution (Topological-to-Tool Mapping)")
    intents = [
        "Deploy a web service on Render with auto-deploy",
        "Perform a complex SQL query on Supabase",
        "Find the documentation for the Transformers library",
        "Analyze a neural network weights tensor with PyTorch",
        "Read a large dataset using the Polars library",
        "Generate a statistical visualization using Seaborn"
    ]

    for intent in intents:
        plan = bridge.generate_agentic_plan(intent)
        print(f"  Intent: '{intent[:50]}...'")
        print(f"    - Domain Hint: {plan['domain_hint']}")
        print(f"    - Topological Coord: {plan['topological_coord']}")
        print(f"    - Resolved Action: {plan['resolved_action']['action']}")
        print(f"    - Selected Resource: {plan['resource_name']} ({plan['resource_type']})")
        print(f"    - Status: {plan['status']}")
        print("-" * 40)

    # 3. Technology Fiber Reflection
    print("\n[3] Technology Fiber Reflection (Effective Techniques)")
    techs = ["RAG", "LoRA", "Mamba", "SES", "Cohomology", "Topological_General_Intelligence"]
    grid = agent.core.ontology.grid
    for tech_name in techs:
        # Find by name
        found = False
        for coord_str, data in grid.items():
            if data["name"] == tech_name:
                print(f"  {tech_name}: {data['payload']}")
                found = True
                break
        if not found:
            print(f"  {tech_name}: [Not Found in Ontology]")

    # 4. Cross-Domain Synthesis
    print("\n[4] Multi-Modal Agentic Synthesis")
    complex_intent = "Deploy a RAG-based application using FastAPI, Supabase, and Render."
    plan = bridge.generate_agentic_plan(complex_intent)
    print(f"  Complex Intent: '{complex_intent}'")
    print(f"  Primary Action: {plan['resolved_action']['action']}")
    print(f"  Primary Resource: {plan['resource_name']} ({plan['resource_type']})")
    print(f"  Reflection: The TGI Agentic Bridge resolves the complex intent into a primary {plan['domain_hint']} action.")

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — TGI Agentic Capacity Expanded  ")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
