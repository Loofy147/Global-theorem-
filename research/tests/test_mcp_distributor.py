import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_mcp_distributor import FSOMCP_Distributor, FSOMCP_Kernel

async def test_mcp_segregation():
    print("Testing MCP Segregation...")
    distributor = FSOMCP_Distributor(m=5)

    # Target fiber 2
    await distributor.deploy_industrial_logic(2, "logic_a", "type_a", "spec_a")

    # Check that only nodes in fiber 2 have the logic
    for coords, node in distributor.nodes.items():
        if node.s_fiber == 2:
            if "logic_a" not in node.logic_traces[2]:
                raise AssertionError(f"Logic 'logic_a' missing in fiber 2 node {coords}")
        else:
            if "logic_a" in node.logic_traces[node.s_fiber]:
                raise AssertionError(f"Logic 'logic_a' found in non-target fiber {node.s_fiber} node {coords}")

async def test_mcp_instruction_wave():
    print("Testing MCP Instruction Wave...")
    distributor = FSOMCP_Distributor(m=5)
    await distributor.deploy_industrial_logic(4, "logic_b", "type_b", "spec_b")

    # Trigger instruction for logic_b
    exec_count = await distributor.trigger_instruction("exec_b", "logic_b", {})

    # m=5, so 5^3 / 5 = 25 nodes should have logic_b
    if exec_count != 25:
        raise AssertionError(f"Expected 25 executions, got {exec_count}")

async def test_kernel_next_hop():
    print("Testing MCP Kernel next_hop...")
    kernel = FSOMCP_Kernel(m=7)
    # Test a coordinate in fiber 0 (sum=0) for color 0 (should have b=2)
    coords = (0, 0, 0)
    nxt = kernel.next_hop(coords, 0)
    # x + 1 + b = 0 + 1 + 2 = 3
    # y - b = 0 - 2 = -2 (mod 7) = 5
    # z = 0
    if nxt != (3, 5, 0):
        raise AssertionError(f"Expected (3, 5, 0), got {nxt}")

    # Test a coordinate in fiber 1 (sum=1) for color 0 (should have b=0)
    coords = (1, 0, 0)
    nxt = kernel.next_hop(coords, 0)
    # x + 1 + b = 1 + 1 + 0 = 2
    # y - b = 0 - 0 = 0
    # z = 0
    if nxt != (2, 0, 0):
        raise AssertionError(f"Expected (2, 0, 0), got {nxt}")

async def run_all():
    try:
        await test_mcp_segregation()
        await test_mcp_instruction_wave()
        await test_kernel_next_hop()
        print("All MCP tests passed!")
    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_all())
