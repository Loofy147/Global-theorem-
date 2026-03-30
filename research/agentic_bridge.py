import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Any, Optional
from research.knowledge_mapper import KnowledgeMapper
from research.action_mapper import ActionMapper

class AgenticBridge:
    """
    The TGI Agentic Bridge.
    Links the topological action space to actual MCP tool signatures and LIBRARY metadata.
    """
    def __init__(self):
        self.ontology = KnowledgeMapper()
        self.actions = ActionMapper()

    def resolve_resource_for_action(self, action_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Finds the most appropriate tool or library for a topological action."""
        action_name = action_data["action"]

        # Mapping topological actions to domains
        domain_map = {
            "DEPLOY_RENDER": "cloud",
            "SQL_SUPABASE": "db",
            "QUERY_DOCS": "docs",
            "NOTIFY": "cloud",
            "LOG": "db",
            "RESPONSE": "docs",
            "COMPUTE": "math",
            "LIFT": "hardware",
            "INGEST": "ui"
        }

        target_domain = domain_map.get(action_name)
        if not target_domain:
            return None

        # Search candidates in both API_MCP and LIBRARY fibers
        candidates = []
        for coord_str, data in self.ontology.grid.items():
            if data["category"] in ["API_MCP", "LIBRARY"] and data["payload"].get("domain") == target_domain:
                candidates.append(data)

        if not candidates:
            return None

        # Select candidate based on focus coordinate
        idx = int(action_data["focus"] * (len(candidates) - 1))
        selected_data = candidates[idx]
        return {
            "type": selected_data["category"],
            "payload": selected_data["payload"]
        }

    def generate_agentic_plan(self, intent: str) -> Dict[str, Any]:
        """Creates a fully resolved agentic plan from a natural language intent."""
        coord = self.actions.resolve_intent(intent)
        action = self.actions.map_coord_to_action(coord)
        res = self.resolve_resource_for_action(action)

        return {
            "intent": intent,
            "topological_coord": coord,
            "resolved_action": action,
            "resource": res["payload"] if res else None,
            "resource_type": res["type"] if res else "NONE",
            "status": "READY_FOR_EXECUTION" if res else "TOPOLOGICAL_NOP"
        }

if __name__ == "__main__":
    bridge = AgenticBridge()
    print("═══ TGI AGENTIC BRIDGE (Library-Aware v2) ═══")
    plan = bridge.generate_agentic_plan("Compute the manifold topology")
    print(f"Plan: {plan}")
