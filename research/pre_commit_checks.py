import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.hardware_awareness import HardwareMapper
from research.action_mapper import ActionMapper
from research.knowledge_mapper import KnowledgeMapper

def verify_system():
    print("═══ TGI PRE-COMMIT VERIFICATION ═══")

    # 1. Hardware Awareness
    hm = HardwareMapper()
    coord = hm.map_to_coordinate()
    assert len(coord) == 3, "Hardware coordinate must be 3D"
    print("[PASS] Hardware Awareness")

    # 2. Action Mapping
    am = ActionMapper()
    action = am.map_coord_to_action(coord)
    assert "action" in action, "Action mapping failed"
    print("[PASS] Action Mapping")

    # 3. Knowledge Base & Dictionary Fiber
    km = KnowledgeMapper()
    assert 5 in km.FIBERS.values(), "LANGUAGE fiber missing"
    assert "LANGUAGE" in km.FIBERS, "LANGUAGE fiber missing"
    print("[PASS] Knowledge Fiber Check")

    # 4. Dictionary Ingestion (Partial)
    count = km.ingest_dictionary("research/wordlist.txt", limit=10)
    assert count > 0, "Dictionary ingestion failed"
    print("[PASS] Dictionary Ingestion")

    print("═══ ALL CHECKS PASSED ═══")

if __name__ == "__main__":
    try:
        verify_system()
    except Exception as e:
        print(f"[FAIL] {e}")
        sys.exit(1)
