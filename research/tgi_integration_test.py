import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tgi_core import TGICore
from tlm import TopologicalLanguageModel
from algebraic import AlgebraicClassifier

def run_integration_test():
    print("═══ TGI / TLM INTEGRATION TEST ═══")

    # 1. Test TGICore against AlgebraicClassifier
    m, k = 3, 3
    tgi = TGICore(m, k)
    print(f"Testing TGICore(m={m}, k={k}): Status={tgi.status['exists']}")
    assert tgi.status['exists'] == "PROVED_POSSIBLE"

    # 2. Test TLM against the same domain
    tlm = TopologicalLanguageModel(m, k)
    is_grammatical = tlm.check_grammar([0, 1, 2])
    print(f"Testing TLM(m={m}, k={k}): Grammatical={is_grammatical}")
    assert is_grammatical == True

    # 3. Verify Obstruction Handling
    m_obs, k_obs = 4, 3
    tgi_obs = TGICore(m_obs, k_obs)
    print(f"Testing TGICore(m={m_obs}, k={k_obs}): Status={tgi_obs.status['exists']}")
    assert tgi_obs.status['exists'] == "PROVED_IMPOSSIBLE"

    tlm_obs = TopologicalLanguageModel(m_obs, k_obs)
    gen = tlm_obs.generate("abcd", 10)
    print(f"Testing TLM(m={m_obs}, k={k_obs}): Result={gen}")
    assert "TOPOLOGICAL_ERROR" in gen

    print("═══ INTEGRATION SUCCESSFUL ═══")

if __name__ == "__main__":
    run_integration_test()
