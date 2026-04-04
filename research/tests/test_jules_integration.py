import pytest
import asyncio
from research.jules_behaviors import plan_execute_verify, autopoietic_synthesis, get_jules_specs

@pytest.mark.asyncio
async def test_plan_execute_verify():
    result = await plan_execute_verify("Fix Render Deployment")
    assert result == "Success"

@pytest.mark.asyncio
async def test_autopoietic_synthesis():
    logic = await autopoietic_synthesis((1, 2, 3))
    assert "def synthesized_logic(): pass" in logic

def test_jules_specs():
    specs = get_jules_specs()
    assert specs["name"] == "Jules"
    assert "Plan-Execute-Verify" in specs["protocols"]
