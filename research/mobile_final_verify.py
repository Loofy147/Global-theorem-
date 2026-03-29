import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.mobile_tgi_agent import MobileTGIAgent
from research.tlm import TopologicalLanguageModel

def verify():
    print("═══ TGI MOBILE FINAL VERIFICATION ═══")

    # 1. Mobile Agent
    ma = MobileTGIAgent()
    res = ma.mobile_query("Check temperature and generate response")
    assert "hw_coord" in res
    assert "resolved_action" in res
    print("[PASS] Mobile Agent Integration")

    # 2. Ontology-Grounded TLM
    tlm = TopologicalLanguageModel(m=25, k=3)
    gen = tlm.generate("Topology is", 10)
    assert len(gen) > len("Topology is")
    print("[PASS] Grounded TLM Generation")

    print("═══ ALL MOBILE CORES STABLE ═══")

if __name__ == "__main__":
    verify()
