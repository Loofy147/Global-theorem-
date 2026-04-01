import pytest
from research.action_mapper import ActionMapper

@pytest.fixture
def am():
    return ActionMapper(m=255)

def test_initialization(am):
    assert am.m == 255
    assert 0 in am.action_space
    assert am.action_space[0] == "DEPLOY_RENDER"

def test_map_coord_to_action(am):
    coord = (0, 0, 0)
    res = am.map_coord_to_action(coord)
    assert "action" in res
    assert "intensity" in res
    assert "focus" in res
    # (0+0+0) % len(action_space) = 0
    assert res["action"] == "DEPLOY_RENDER"

def test_map_coord_to_action_sum(am):
    # len(action_space) is 11 (0..10)
    coord = (1, 1, 1) # sum=3
    res = am.map_coord_to_action(coord)
    assert res["action"] == "NOTIFY"

def test_resolve_intent_tlm(am):
    # This should use TLM coordinate lifting
    intent = "Deploy RAG service"
    coord = am.resolve_intent(intent)
    assert isinstance(coord, tuple)
    assert len(coord) == 3
    assert all(0 <= c < am.m for c in coord)

def test_path_to_action_sequence(am):
    path = [(0, 0, 0), (1, 1, 1)]
    seq = am.path_to_action_sequence(path)
    assert len(seq) == 2
    assert seq[0]["action"] == "DEPLOY_RENDER"
    assert seq[1]["action"] == "NOTIFY"
