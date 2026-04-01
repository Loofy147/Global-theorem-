import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import List, Dict, Any, Optional, Tuple
from research.agentic_bridge import AgenticBridge
from research.action_mapper import ActionMapper

class ActionExecutor:
    """
    TGI Action Executor (Phase 8 Completion).
    Handles real execution of agentic plans and establishes the feedback loop.
    Guided by Law VII (Basin Escape) and Law IX (Hardware Grounding).
    """
    def __init__(self):
        from research.knowledge_mapper import KnowledgeMapper
        self.ontology = KnowledgeMapper()

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a single step of an agentic plan."""
        action = step["action"]
        resource = step["resource"]
        result = {"status": "SUCCESS", "output": f"Executed {action} via {resource}"}

        # Mock execution for the TGI manifold
        # In a real scenario, this would call the MCP tools or internal cores
        if step["type"] == "CORE":
            result["output"] = f"Core transition to {resource} successful."
        elif step["type"] == "MCP":
            result["output"] = f"MCP Tool {resource} invoked with success."
        elif step["type"] == "INTERNAL":
            result["output"] = f"Internal signal {resource} broadcasted."

        # Feedback Loop: Re-ingest the result into the ontology (Law VII)
        self.ontology.ingest_concept("DATASET", f"LOG_{action}_{resource}", result)
        self.ontology.save_state()

        return result

    def execute_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Executes a full multi-step plan and returns the audit trail."""
        results = []
        for step in plan:
            res = self.execute_step(step)
            results.append({**step, "result": res})
        return results

class TopologicalActionEngine:
    """
    TGI Agentic Action Engine.
    Executes and resolves multi-step topological paths into coherent agentic plans.
    """
    def __init__(self):
        self.bridge = AgenticBridge()
        self.mapper = ActionMapper()
        self.executor = ActionExecutor()

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

    print(f"\n═══ EXECUTING PLAN (Feedback Loop) ═══")
    results = engine.executor.execute_plan(plan)
    for res in results:
        print(f"Step {res['step']} Result: {res['result']['status']} - {res['result']['output']}")
