import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, Any, Tuple
# Use local mocks if TGI agent (numpy) is missing for CLI-only test
try:
    from research.tgi_agent import TGIAgent
    core_ready = True
except ImportError:
    core_ready = False

from research.hardware_awareness import HardwareMapper
from research.action_mapper import ActionMapper

class MobileTGIAgent:
    """
    The Mobile-First TGI Agent.
    Combines the core TGI Reasoning with Hardware Awareness and Agentic Action Mapping.
    """
    def __init__(self):
        self.tgi_agent = TGIAgent() if core_ready else None
        self.hardware = HardwareMapper()
        self.actions = ActionMapper()

    def mobile_query(self, text: str) -> Dict[str, Any]:
        """
        Processes a natural language query with full hardware-awareness.
        """
        # 1. Get Hardware Context
        hw_coord = self.hardware.map_to_coordinate()
        hw_state = self.hardware.get_system_state()

        # 2. Lift Text Intent
        intent_coord = self.actions.resolve_intent(text)

        # 3. Core TGI Reasoning
        tgi_response = self.tgi_agent.query(text) if self.tgi_agent else "[TGI_CORE: UNAVAILABLE (NUMPY_MISSING)]"

        # 4. Map the 'final state' to an action.
        action = self.actions.map_coord_to_action(intent_coord)

        return {
            "query": text,
            "hw_state": hw_state,
            "hw_coord": hw_coord,
            "tgi_raw": tgi_response,
            "resolved_action": action,
            "thermal_entropy": self.hardware.measure_thermal_entropy()
        }

if __name__ == "__main__":
    mobile_agent = MobileTGIAgent()
    print("═══ MOBILE TGI AGENT PROTOTYPE ═══")
    res = mobile_agent.mobile_query("Check system health and notify")
    print(f"Query: {res['query']}")
    print(f"HW State: {res['hw_state']}")
    print(f"Resolved Action: {res['resolved_action']}")
    print(f"TGI Response: {res['tgi_raw']}")
