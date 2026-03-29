import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Any, Optional
from research.knowledge_mapper import KnowledgeMapper
from research.action_mapper import ActionMapper

class AgenticBridge:
    """
    The TGI Agentic Bridge.
    Links the topological action space to actual MCP tool signatures and parameters.
    """
    def __init__(self):
        self.ontology = KnowledgeMapper()
        self.actions = ActionMapper()

    def resolve_tool_for_action(self, action_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Finds the most appropriate tool in the ontology for a topological action."""
        action_name = action_data["action"]

        # Mapping topological actions to domains
        # Broaden mapping to capture more intents
        domain_map = {
            "DEPLOY_RENDER": "cloud",
            "SQL_SUPABASE": "db",
            "QUERY_DOCS": "docs",
            "NOTIFY": "cloud",
            "LOG": "db",
            "RESPONSE": "docs"
        }

        target_domain = domain_map.get(action_name)
        if not target_domain:
            return None

        candidates = []
        for coord_str, data in self.ontology.grid.items():
            if data["category"] == "API_MCP" and data["payload"].get("domain") == target_domain:
                candidates.append(data["payload"])

        if not candidates:
            return None

        # Select tool based on focus coordinate
        idx = int(action_data["focus"] * (len(candidates) - 1))
        return candidates[idx]

    def generate_agentic_plan(self, intent: str) -> Dict[str, Any]:
        """Creates a fully resolved agentic plan from a natural language intent."""
        coord = self.actions.resolve_intent(intent)
        action = self.actions.map_coord_to_action(coord)
        tool = self.resolve_tool_for_action(action)

        return {
            "intent": intent,
            "topological_coord": coord,
            "resolved_action": action,
            "mcp_tool": tool,
            "status": "READY_FOR_EXECUTION" if tool else "TOPOLOGICAL_NOP"
        }

if __name__ == "__main__":
    bridge = AgenticBridge()
    print("═══ TGI AGENTIC BRIDGE ═══")
    plan = bridge.generate_agentic_plan("Deploy the backend to Render")
    print(f"Plan: {plan}")
