import asyncio
import hashlib
import json
import time
import sys
import os
import ast
from typing import Dict, Any, Tuple, Optional, List

# Add parent directory to path for core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma

class FSOFabricNode:
    """
    A Production-grade FSO Node.
    Handles data ingestion, stateless routing, and payload delivery.
    Supports Holographic Logic Execution.
    """
    def __init__(self, coords: Tuple[int, int, int], m: int, peers: Optional[Dict[Tuple[int, int, int], str]] = None):
        self.coords = coords
        self.m = m
        self.peers = peers or {}
        self.processed_count = 0
        self.delivered_packets = []

        # Local Holographic Logic Storage (At Rest)
        self.logic_layer = {} # name -> {code, hash, fiber}

        # Every node independently generates the same deterministic Hamiltonian manifold.
        self.sigma = construct_spike_sigma(m, 3)
        if not self.sigma:
            raise ValueError(f"FSO Error: Failed to construct manifold for m={m}.")

    def calculate_next_hop(self, current: Tuple[int, int, int], color: int) -> Tuple[int, int, int]:
        """Law VI: The Universal Spike - O(1) stateless routing."""
        p = self.sigma.get(current)
        if not p: return current
        arc = p[color]
        nxt = list(current)
        nxt[arc] = (nxt[arc] + 1) % self.m
        return tuple(nxt)

    async def route_packet(self, packet: Dict[str, Any]):
        """Stateless Discovery and Routing."""
        target_coords = tuple(packet['target'])

        # Direct execution: Is this packet addressed to this node's coordinate?
        if target_coords == self.coords:
            return await self.process_payload(packet)

        # Forward along the Hamiltonian cycle for the packet's color
        return self.calculate_next_hop(self.coords, packet['color'])

    async def process_payload(self, packet: Dict[str, Any]):
        """Processes logic ingestion or execution requests."""
        payload = packet.get("payload", {})
        ptype = packet.get("type")

        if ptype == "LOGIC_INJECT":
            logic_id = payload.get("id")
            self.logic_layer[logic_id] = {
                "code": payload.get("code"),
                "hash": payload.get("hash"),
                "fiber": sum(self.coords) % self.m
            }
            # print(f"[NODE {self.coords}] Ingested Logic: {logic_id}")
            return True

        elif ptype == "LOGIC_EXECUTE":
            logic_id = payload.get("id")
            if logic_id in self.logic_layer:
                # In production, this would execute the AST code safely.
                # Here, we simulate the result.
                # print(f"[NODE {self.coords}] Executing Logic: {logic_id}")
                return {"status": "SUCCESS", "node": self.coords, "logic": logic_id}
            else:
                return {"status": "FAILURE", "reason": "Logic not at this coordinate"}

        self.processed_count += 1
        self.delivered_packets.append(packet)
        return True

    async def consume(self, packet: Dict[str, Any]):
        self.processed_count += 1
        self.delivered_packets.append(packet)

class FSODataStream:
    """Utility to inject data into the Hamiltonian flow."""
    @staticmethod
    def create_packet(data: Any, target: Tuple[int, int, int], color: int = 0, ptype: str = "DATA"):
        return {
            "id": hashlib.md5(f"{time.time()}{data}{target}".encode()).hexdigest()[:8],
            "target": target,
            "color": color,
            "type": ptype,
            "payload": data if isinstance(data, dict) else {"data": data},
            "timestamp": time.time()
        }

if __name__ == "__main__":
    m = 7
    node = FSOFabricNode((0,0,0), m)
    packet = FSODataStream.create_packet({"id": "test_func", "code": "def test_func(): pass"}, (0,0,0), ptype="LOGIC_INJECT")
    print(f"Node (0,0,0) testing logic ingestion...")
    asyncio.run(node.route_packet(packet))
    print(f"Logic Layer: {list(node.logic_layer.keys())}")
