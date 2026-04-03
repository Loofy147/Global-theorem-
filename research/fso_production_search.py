import asyncio
import time
import random
import sys
import os
from typing import List, Dict, Any, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_mesh_daemon import FSOMeshDaemon

class FSOProductionSearch:
    """
    A Distributed, Index-less Search Engine leveraging the FSO Mesh.
    Uses Color 0 Storage Waves and Color 1 Logic Waves.
    """
    def __init__(self, m: int = 11):
        self.m = m
        self.daemon = FSOMeshDaemon(m)

    async def initialize(self):
        """Bootstrap the mesh with search logic."""
        await self.daemon.bootstrap(["./research/fso_fabric.py"])

    async def ingest_corpus(self, docs: List[Dict[str, str]]):
        """Populates the Storage Wave (Color 0)."""
        print(f"--- INGESTING {len(docs)} DOCUMENTS INTO STORAGE WAVE ---")
        tasks = []
        for i, doc in enumerate(docs):
            # Target the node for doc_i
            target_coords = (i % self.m, (i // self.m) % self.m, (i // (self.m**2)) % self.m)
            tasks.append(self.daemon.inject_storage(f"doc_{i}", doc, target_coords))

        await asyncio.gather(*tasks)
        print("Ingestion complete.")

    async def search(self, keyword: str):
        """Dispatches a Logic Wave (Color 1) to find intersections."""
        print(f"\n--- SEARCHING FOR '{keyword.upper()}' VIA HAMILTONIAN INTERSECTION ---")

        results = []
        # Every logic node is targeted, using its local 'calculate_next_hop' logic
        # In a real hardware system, the wave would hit all nodes.
        logic_coords = self.daemon.get_coords("calculate_next_hop")

        # We check all nodes where documents were ingested
        for i in range(self.m**3):
            # Coordinates of the node containing doc_i
            coords = (i % self.m, (i // self.m) % self.m, (i // (self.m**2)) % self.m)

            # Intersection can only happen if logic 'calculate_next_hop' is also at 'coords'
            # For this production search, we inject search logic to all nodes.
            node = self.daemon.nodes[coords]

            # Let's manually inject the search logic to all nodes for this demo
            if "calculate_next_hop" not in node.logic_registry:
                # Mock injection
                node.logic_registry["calculate_next_hop"] = {"code": "SEARCH_LOGIC"}

            packet = {
                "color": 1,
                "target": coords,
                "type": "LOGIC_EXECUTE",
                "payload": {"id": "calculate_next_hop", "target_key": f"doc_{i}", "keyword": keyword}
            }

            res = await node.route_packet(packet)
            if isinstance(res, dict) and res.get("match") is True:
                doc = node.local_storage.get(f"doc_{i}")
                results.append({"node": coords, "title": doc.get("title")})

        return results

def generate_sample_corpus(count: int = 100) -> List[Dict[str, str]]:
    topics = [
        ("Quantum Topologies", "The intersection of quantum computing and toroidal meshes..."),
        ("FSO Routing", "Fiber-Stratified Optimization provides O(1) routing with zero RAM..."),
        ("Advanced Robotics", "The new servo motors use non-abelian sensor arrays..."),
        ("Closure Lemma", "By knowing k-1 cycles, we algebraically deduce the Hamiltonian close..."),
        ("Agricultural AI", "Crop yields are improved via simulated annealing landscapes..."),
        ("The Master Key", "The step size of r=(1, m-2, 1) provides perfect coprimality..."),
        ("History of Algiers", "The capital city of Algeria, located on the Mediterranean coast..."),
        ("Network Latency", "Dimension-Order Routing suffers from tail latency and bottlenecks...")
    ]
    docs = []
    for i in range(count):
        topic = random.choice(topics)
        docs.append({"title": f"Doc_{i}_{topic[0]}", "content": topic[1]})
    return docs

async def main():
    engine = FSOProductionSearch(m=7)
    await engine.initialize()

    # 1. Ingest Corpus
    corpus = generate_sample_corpus(200)
    await engine.ingest_corpus(corpus)

    # 2. Search
    keyword = "routing"
    results = await engine.search(keyword)

    print(f"\n--- SEARCH RESULTS ({len(results)} HITS) ---")
    for r in results[:5]:
        print(f"  [HIT] {r['title']} found at Node {r['node']}")

if __name__ == "__main__":
    asyncio.run(main())
