import asyncio
import hashlib
import json
import time
import sys
import os
from typing import Dict, Any, Tuple, Optional, List

# Add parent directory to path for core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma

class FSOFabricNode:
    """
    A Production-grade FSO Node.
    Handles data ingestion, stateless routing, and payload delivery.
    """
    def __init__(self, coords: Tuple[int, int, int], m: int, peers: Optional[Dict[Tuple[int, int, int], str]] = None):
        self.coords = coords
        self.m = m
        self.peers = peers or {}  # Maps (x,y,z) to connection strings
        self.inbox = asyncio.Queue()
        self.processed_count = 0
        self.delivered_packets = []

        # Every node independently generates the same deterministic Hamiltonian manifold.
        self.sigma = construct_spike_sigma(m, 3)
        if not self.sigma:
            raise ValueError(f"FSO Error: Failed to construct manifold for m={m}. (Odd m required)")

    def get_fiber(self, pos: Tuple[int, int, int]) -> int:
        """Law I: The Fibration."""
        return sum(pos) % self.m

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
        if target_coords == self.coords:
            await self.consume(packet)
            return None # Delivered

        # Determine next hop along the Hamiltonian cycle for the packet's color
        return self.calculate_next_hop(self.coords, packet['color'])

    async def receive_packet(self, packet: Dict[str, Any]):
        """Entry point for incoming data."""
        await self.inbox.put(packet)

    async def run_router_loop(self):
        """Main loop for processing and forwarding packets."""
        while True:
            packet = await self.inbox.get()
            target_coords = tuple(packet['target'])

            if target_coords == self.coords:
                await self.consume(packet)
            else:
                next_coords = self.calculate_next_hop(self.coords, packet['color'])
                await self.forward(next_coords, packet)

            self.inbox.task_done()

    async def consume(self, packet: Dict[str, Any]):
        """Law II: Stateless Discovery."""
        self.processed_count += 1
        self.delivered_packets.append(packet)
        # print(f"[NODE {self.coords}] Packet {packet['id']} consumed. Payload: {packet['data']}")

    async def forward(self, next_coords: Tuple[int, int, int], packet: Dict[str, Any]):
        """Logic for physical transmission (Simulated)."""
        peer_addr = self.peers.get(next_coords)
        if peer_addr:
            # In a real system, we'd use TCP/UDP/RDMA here
            # print(f"[NODE {self.coords}] Forwarding {packet['id']} to {next_coords} ({peer_addr})")
            pass
        else:
            # In simulation, we just return the next hop to the driver
            pass

class FSODataStream:
    """Utility to inject data into the Hamiltonian flow."""
    @staticmethod
    def create_packet(data: Any, target: Tuple[int, int, int], color: int = 0):
        return {
            "id": hashlib.md5(f"{time.time()}{data}{target}".encode()).hexdigest()[:8],
            "target": target,
            "color": color,
            "data": data,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    # Small test for verify correctness
    m = 7
    node = FSOFabricNode((0,0,0), m)
    packet = FSODataStream.create_packet("SYS_CHECK", (3,3,3), color=2)

    print(f"Node (0,0,0) routing packet for (3,3,3) on Color 2...")
    nxt = asyncio.run(node.route_packet(packet))
    print(f"Next Hop: {nxt}")
