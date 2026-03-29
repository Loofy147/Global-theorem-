import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.hardware_awareness import HardwareMapper
from research.action_mapper import ActionMapper
from research.knowledge_mapper import KnowledgeMapper

def test_mobile_integration():
    print("═══ TGI MOBILE INTEGRATION TEST ═══")

    # 1. Hardware State -> Coordinate
    hm = HardwareMapper()
    coord = hm.map_to_coordinate()
    print(f"[TEST] System Coordinate: {coord}")

    # 2. Coordinate -> Action
    am = ActionMapper()
    action = am.map_coord_to_action(coord)
    print(f"[TEST] Mapped Action: {action}")

    # 3. Knowledge Base Check (Dictionary Fiber)
    km = KnowledgeMapper()
    # Check if a word was ingested into fiber 5 (LANGUAGE)
    sample_word = "apple"
    km.ingest_concept("LANGUAGE", sample_word, "Test Entry")
    found_coord = km._find_coord(sample_word)
    print(f"[TEST] Sample Word '{sample_word}' mapped to {found_coord}")

    # 4. Intent Lifting
    intent = "Launch the TGI manifold analysis"
    intent_coord = am.resolve_intent(intent)
    intent_action = am.map_coord_to_action(intent_coord)
    print(f"[TEST] Intent '{intent}' lifted to {intent_coord} -> {intent_action}")

    print("═══ TEST COMPLETE ═══")

if __name__ == "__main__":
    test_mobile_integration()
