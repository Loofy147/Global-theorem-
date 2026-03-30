import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import List, Dict, Any, Optional, Tuple
from research.agentic_bridge import AgenticBridge
from research.action_mapper import ActionMapper

class TopologicalActionEngine:
    """
    TGI Agentic Action Engine.
    Executes and resolves multi-step topological paths into coherent agentic plans.
    """
    def __init__(self):
        self.bridge = AgenticBridge()
        self.mapper = ActionMapper()

    def resolve_path_to_plan(self, path: List[Tuple[int, ...]], base_intent: str) -> List[Dict[str, Any]]:
        """Resolves a sequence of coordinates into a multi-step execution plan."""
        plan = []
        seen_resources = set()

        for coord in path:
            action = self.mapper.map_coord_to_action(coord)
            res = self.bridge.resolve_resource_for_action(action)

            if res and res["name"] not in seen_resources:
                step = {
                    "step": len(plan) + 1,
                    "action": action["action"],
                    "resource": res["name"],
                    "type": res["type"],
                    "payload": res["payload"]
                }
                plan.append(step)
                seen_resources.add(res["name"])

            if len(plan) >= 5: # Limit plan size for demo
                break

        return plan

if __name__ == "__main__":
    from research.tlm import TopologicalLanguageModel
    tlm = TopologicalLanguageModel(m=25, k=3)
    engine = TopologicalActionEngine()

    intent = "Deploy a RAG service with observability"
    path = tlm.generate_path(intent, 20)
    plan = engine.resolve_path_to_plan(path, intent)

    print(f"═══ TGI ACTION ENGINE PLAN ═══")
    print(f"Intent: {intent}")
    for step in plan:
        print(f"Step {step['step']}: {step['action']} using {step['resource']} ({step['type']})")
