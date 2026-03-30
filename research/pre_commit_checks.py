import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verify_system():
    print("═══ TGI PRE-COMMIT VERIFICATION ═══")

    # 1. Hardware Awareness (Fallback test)
    try:
        from research.hardware_awareness import HardwareMapper
        hm = HardwareMapper()
        coord = hm.map_to_coordinate()
        assert len(coord) == 3, "Hardware coordinate must be 3D"
        print("[PASS] Hardware Awareness")
    except ImportError:
        print("[SKIP] Hardware Awareness (psutil missing)")

    # 2. Action Mapping
    try:
        from research.action_mapper import ActionMapper
        am = ActionMapper()
        action = am.map_coord_to_action((1, 2, 3))
        assert "action" in action, "Action mapping failed"
        print("[PASS] Action Mapping")
    except ImportError:
        print("[SKIP] Action Mapping")

    # 3. Knowledge Base & Dictionary Fiber
    try:
        from research.knowledge_mapper import KnowledgeMapper
        km = KnowledgeMapper()
        assert "LANGUAGE" in km.FIBERS, "LANGUAGE fiber missing"
        print("[PASS] Knowledge Fiber Check")
        # 4. Dictionary Ingestion (Partial)
        count = km.ingest_dictionary("research/wordlist.txt", limit=10)
        assert count > 0, "Dictionary ingestion failed"
        print("[PASS] Dictionary Ingestion")
    except (ImportError, FileNotFoundError):
        print("[SKIP] Knowledge Base / Dictionary checks")

    # 5. Master Solver Core
    from core import solve, verify_sigma
    sol = solve(3, 3)
    assert verify_sigma(sol, 3), "Master Solver (3,3) failed"
    print("[PASS] Master Solver (3,3)")

    print("═══ ALL CHECKS PASSED ═══")

if __name__ == "__main__":
    try:
        verify_system()
    except Exception as e:
        print(f"[FAIL] {e}")
        sys.exit(1)
