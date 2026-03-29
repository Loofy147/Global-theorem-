import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tgi_core import TGICore
from tlm import TopologicalLanguageModel

def run_integration_test():
    print("═══ ENHANCED TGI / TLM INTEGRATION TEST ═══")

    # 1. Test TGICore Path Lifting (Core B)
    m, k = 3, 3
    tgi = TGICore(m, k)
    next_p = tgi.lift_path([0, 1, 2])
    print(f"Testing TGICore(m={m}, k={k}): Lifted next point = {next_p}")
    assert next_p is not None

    # 2. Test TLM Path Generation
    tlm = TopologicalLanguageModel(m, k)
    gen = tlm.generate("abc", 5)
    print(f"Testing TLM(m={m}, k={k}): Generated completion = '{gen}'")
    assert len(gen) > 3

    # 3. Test Obstruction Handling
    m_obs, k_obs = 4, 3
    tgi_obs = TGICore(m_obs, k_obs)
    lift_obs = tgi_obs.lift_path([0, 1, 2])
    print(f"Testing TGICore(m={m_obs}, k={k_obs}): Lift on obstructed manifold = {lift_obs}")
    assert lift_obs is None

    tlm_obs = TopologicalLanguageModel(m_obs, k_obs)
    gen_obs = tlm_obs.generate("abcd", 5)
    print(f"Testing TLM(m={m_obs}, k={k_obs}): Result on obstructed manifold = '{gen_obs}'")
    assert "TOPOLOGICAL_ERROR" in gen_obs

    # 4. Verify Intelligence IQ (W6)
    iq = tgi.measure_intelligence()
    print(f"Testing TGI IQ (m=3, k=3): IQ = {iq:.4f}")
    assert 0 < iq < 1

    print("═══ ENHANCED INTEGRATION SUCCESSFUL ═══")

if __name__ == "__main__":
    run_integration_test()
