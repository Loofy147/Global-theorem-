import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Any, Optional
from research.knowledge_mapper import KnowledgeMapper
from research.action_mapper import ActionMapper

class AgenticBridge:
    """
    The TGI Agentic Bridge (Upgraded v4).
    Links the topological action space to actual MCP tool signatures and LIBRARY metadata.
    """
    def __init__(self):
        self.ontology = KnowledgeMapper()
        self.actions = ActionMapper()

    def resolve_resource_for_action(self, action_data: Dict[str, Any], domain_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
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

        target_domain = domain_hint or domain_map.get(action_name)
        if not target_domain:
            return None

        # Search candidates in both API_MCP and LIBRARY fibers
        candidates = []
        for coord_str, data in self.ontology.grid.items():
            if data["category"] in ["API_MCP", "LIBRARY"]:
                payload = data.get("payload", {})
                if isinstance(payload, dict) and payload.get("domain") == target_domain:
                    candidates.append(data)
                elif isinstance(payload, str) and target_domain in payload.lower():
                    candidates.append(data)

        if not candidates:
            # Fallback to general search if no domain match
            for coord_str, data in self.ontology.grid.items():
                if data["category"] in ["API_MCP", "LIBRARY"]:
                    candidates.append(data)

        if not candidates:
            return None

        # Sort candidates to ensure deterministic selection based on focus
        candidates.sort(key=lambda x: x["name"])

        # Select candidate based on focus coordinate
        idx = int(action_data.get("focus", 0.5) * (len(candidates) - 1))
        selected_data = candidates[idx]
        return {
            "type": selected_data["category"],
            "name": selected_data["name"],
            "payload": selected_data["payload"]
        }

    def generate_agentic_plan(self, intent: str) -> Dict[str, Any]:
        """Creates a fully resolved agentic plan from a natural language intent."""
        coord = self.actions.resolve_intent(intent)
        action = self.actions.map_coord_to_action(coord)

        # Heuristic domain detection from intent
        low_intent = intent.lower()
        domain_hint = None
        if any(w in low_intent for w in ["deploy", "render", "cloud", "service"]): domain_hint = "cloud"
        elif any(w in low_intent for w in ["db", "sql", "supabase", "database", "table"]): domain_hint = "db"
        elif any(w in low_intent for w in ["docs", "library", "query", "numpy", "documentation"]): domain_hint = "docs"
        elif any(w in low_intent for w in ["ai", "neural", "pytorch", "tensorflow", "transform"]): domain_hint = "ai"
        elif any(w in low_intent for w in ["data", "pandas", "polars"]): domain_hint = "data"
        elif any(w in low_intent for w in ["viz", "plot", "matplotlib", "seaborn", "plotly"]): domain_hint = "viz"

        res = self.resolve_resource_for_action(action, domain_hint=domain_hint)

        return {
            "intent": intent,
            "topological_coord": coord,
            "resolved_action": action,
            "domain_hint": domain_hint,
            "resource_name": res["name"] if res else "NONE",
            "resource_type": res["type"] if res else "NONE",
            "resource_payload": res["payload"] if res else None,
            "status": "READY_FOR_EXECUTION" if res else "TOPOLOGICAL_NOP"
        }

if __name__ == "__main__":
    bridge = AgenticBridge()
    print("═══ TGI AGENTIC BRIDGE (Upgraded v4) ═══")
    test_intents = [
        "Deploy a new web service on Render",
        "Query the Supabase database",
        "Read documentation for NumPy",
        "Analyze this neural network",
        "Process some data with Polars",
        "Create a plot with Matplotlib"
    ]
    for intent in test_intents:
        plan = bridge.generate_agentic_plan(intent)
        print(f"Intent: {intent} (Domain Hint: {plan['domain_hint']})")
        print(f"  Action: {plan['resolved_action']['action']}, Resource: {plan['resource_name']} ({plan['resource_type']})")
