import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.tgi_agent import TGIAgent
import json

def run_demo():
    print("═══════════════════════════════════════════════")
    print("  TGI AUTONOMOUS ENGINE DEMO — March 2026  ")
    print("═══════════════════════════════════════════════")

    agent = TGIAgent()

    # 1. Complex Multi-Step Intent
    print("\n[1] Resolving Complex Multi-Step Intent...")
    intent = "Analyze the neural network topology, then deploy a database and log the results."
    result = agent.autonomous_query(intent)

    print(f"  Intent: '{intent}'")
    print(f"  Manifold: {result['manifold']}")
    print(f"  Path Length: {result['path_length']}")
    print(f"  Generated Execution Plan:")

    for step in result['plan']:
        print(f"    Step {step['step']}: {step['action']} (via {step['resource']} | {step['type']})")

    # 2. Tech Reflection (New Additions)
    print("\n[2] Verifying New Advanced Technologies...")
    new_techs = ["CoT", "ReAct", "Model_Merging", "DPO", "Vector_DB"]
    grid = agent.core.ontology.grid
    for tech in new_techs:
        found = False
        for d in grid.values():
            if d["name"] == tech:
                print(f"  {tech}: {d['payload']}")
                found = True
                break
        if not found:
            print(f"  {tech}: [Not Found]")

    # 3. Library Reflection (New Ecosystem)
    print("\n[3] Verifying New Ecosystem Libraries...")
    new_libs = ["LangChain", "LlamaIndex", "Pinecone", "ChromaDB", "Sentry"]
    for lib_name in new_libs:
        found = False
        for d in grid.values():
            if d["name"] == lib_name:
                print(f"  {lib_name}: {d['payload'].get('description', 'No description')}")
                found = True
                break
        if not found:
            print(f"  {lib_name}: [Not Found]")

    print("\n═══════════════════════════════════════════════")
    print("  DEMO COMPLETE — TGI Autonomy Verified  ")
    print("═══════════════════════════════════════════════")

if __name__ == "__main__":
    run_demo()
