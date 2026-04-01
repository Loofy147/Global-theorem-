import pytest
from unittest.mock import patch
from research.tgi_agent import TGIAgent

@pytest.fixture
def agent():
    return TGIAgent()

def test_hardware_adaptation_high_memory(agent):
    with patch('research.hardware_awareness.HardwareMapper.get_system_state') as mock_state:
        mock_state.return_value = {"cpu": 10.0, "memory": 90.0, "battery": 100.0}
        # Intent that would normally use m=256, k=4 (knowledge)
        # But we'll use language (m=25, k=3)
        res = agent.query("Adaptive Test", hierarchical=False)
        assert "[TGI_RESPONSE: LIFT_SUCCESS]" in res

def test_hardware_adaptation_high_cpu(agent):
    with patch('research.hardware_awareness.HardwareMapper.get_system_state') as mock_state:
        mock_state.return_value = {"cpu": 95.0, "memory": 10.0, "battery": 100.0}
        res = agent.query("Adaptive Test", hierarchical=False)
        assert "[TGI_RESPONSE: LIFT_SUCCESS]" in res

def test_autonomous_query(agent):
    res = agent.autonomous_query("Deploy a service")
    assert "plan" in res
    assert len(res["plan"]) > 0
