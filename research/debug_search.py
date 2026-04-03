import asyncio
from research.fso_production_search import FSOProductionSearch

async def debug():
    engine = FSOProductionSearch(m=3)
    await engine.initialize()

    # Check if 'calculate_next_hop' is in the logic registry of its target node
    target_coords = engine.daemon.get_coords("calculate_next_hop")
    node = engine.daemon.nodes[target_coords]
    print(f"Logic Registry at {target_coords}: {list(node.logic_registry.keys())}")

    # Ingest one document at that coordinate
    await engine.daemon.inject_storage("doc_0", {"title": "Test", "content": "routing logic"}, target_coords)
    print(f"Storage at {target_coords}: {list(node.local_storage.keys())}")

    # Try execution
    packet = {
        "color": 1,
        "target": target_coords,
        "type": "LOGIC_EXECUTE",
        "payload": {"id": "calculate_next_hop", "target_key": "doc_0", "keyword": "routing"}
    }
    res = await node.route_packet(packet)
    print(f"Execution result: {res}")

if __name__ == "__main__":
    asyncio.run(debug())
