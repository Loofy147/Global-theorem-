import pytest
from research.agentic_bridge import AgenticBridge

@pytest.fixture
def bridge():
    return AgenticBridge()

def test_resolve_intent_math(bridge):
    res = bridge.resolve_intent("Solve x^2 + 1 = 0")
    assert res["primary_action"] == "SYMBOLIC_REASON"
    assert "G_9^3" in res["manifold"] # TGIParser maps math to m=9, k=3

def test_resolve_intent_language(bridge):
    res = bridge.resolve_intent("Hello world")
    assert res["primary_action"] == "TLM_GENERATE"
    assert "G_25^3" in res["manifold"] # TGIParser maps language to m=25, k=3

def test_resolve_intent_vision(bridge):
    res = bridge.resolve_intent("Analyze image.png")
    assert res["primary_action"] == "IMAGE_LIFT"
    assert "G_255^5" in res["manifold"] # TGIParser maps vision to m=255, k=5

def test_resolve_resource_mcp(bridge):
    action_data = {"action": "DEPLOY_RENDER"}
    res = bridge.resolve_resource_for_action(action_data)
    assert res["name"] == "render_create_web_service"
    assert res["type"] == "MCP"

def test_resolve_resource_library(bridge):
    action_data = {"action": "COMPUTE"}
    res = bridge.resolve_resource_for_action(action_data)
    assert res["name"] == "numpy"
    assert res["type"] == "LIBRARY"

def test_resolve_resource_core(bridge):
    action_data = {"action": "INGEST"}
    res = bridge.resolve_resource_for_action(action_data)
    assert res["name"] == "KnowledgeMapper"
    assert res["type"] == "CORE"

def test_generate_agentic_plan(bridge):
    plan = bridge.generate_agentic_plan("Deploy a website")
    assert isinstance(plan, list)
    assert len(plan) > 0
    assert "manifold" in plan[0]
