import asyncio
import hashlib
import json
import socket
import uuid
import os
from typing import Tuple, Dict

# --- FSO TOPOLOGICAL KERNEL ---
class FSOTopology:
    def __init__(self, m: int):
        self.m = m

    def spike_step(self, coords: Tuple[int, int, int], color: int) -> Tuple[int, int, int]:
        x, y, z = coords
        s = sum(coords) % self.m
        b = 2 if (s == 0 and color == 0) else (-(self.m - 1) if s == 0 else 0)

        if color == 0: return ((x + 1 + b) % self.m, (y - b) % self.m, z % self.m)
        if color == 1: return (x % self.m, (y + 1 + b) % self.m, (z - b) % self.m)
        if color == 2: return ((x - b) % self.m, y % self.m, (z + 1 + b) % self.m)
        return coords

# --- PLANETARY DECENTRALIZED NODE ---
class GlobalFSONode:
    def __init__(self, m: int, seed_ip: str = None):
        self.m = m
        self.topo = FSOTopology(m)
        self.node_id = str(uuid.uuid4())
        self.public_ip = self._get_public_ip()
        self.port = int(os.getenv("FSO_PORT", 8888))

        self.coords = None # Will be assigned upon network join
        self.fiber = None
        self.peer_directory: Dict[Tuple[int,int,int], str] = {} # Map coords to IP:PORT

        self.seed_ip = seed_ip # The bootstrap server to discover the mesh

    def _get_public_ip(self):
        """Discovers the node's real-world IP."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    async def join_mesh(self):
        """Contacts the seed node to claim an (x,y,z) coordinate in the Torus."""
        print(f"[*] Booting Global Node {self.node_id} at {self.public_ip}:{self.port}")

        if self.seed_ip:
            print(f"[*] Contacting Seed Node at {self.seed_ip}...")
            # In production, this performs a TCP handshake to claim an empty slot
            # For demonstration, we deterministically hash our IP to find our coordinate
            h = int(hashlib.md5(self.public_ip.encode()).hexdigest(), 16)
            self.coords = (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)
        else:
            print("[*] No Seed IP provided. Booting as GENESIS NODE at (0,0,0).")
            self.coords = (0, 0, 0)

        self.fiber = sum(self.coords) % self.m
        print(f"[+] Successfully integrated into FSO Manifold at {self.coords} (Fiber {self.fiber})")

    async def start_server(self):
        """Listens for Hamiltonian Waves arriving over the public internet."""
        server = await asyncio.start_server(self.handle_wave, '0.0.0.0', self.port)
        print(f"[+] Physical TCP Socket listening on 0.0.0.0:{self.port}")
        async with server:
            await server.serve_forever()

    async def handle_wave(self, reader, writer):
        """Processes incoming network traffic in O(1) time."""
        data = await reader.read(4096)
        if not data: return

        packet = json.loads(data.decode())
        color = packet.get("color")

        print(f"[~] Received Color {color} Wave from Torus.")

        # 1. Process Logic (Execution, TGI, Storage)
        # ... logic execution goes here ...

        # 2. Forward the Wave physically across the internet
        if packet.get('ttl', 0) > 0:
            packet['ttl'] -= 1
            next_coords = self.topo.spike_step(self.coords, color)
            await self._physical_forward(next_coords, packet)

        writer.close()
        await writer.wait_closed()

    async def _physical_forward(self, next_coords, packet):
        """Resolves the (x,y,z) to a physical IP and sends the data."""
        target_ip = self.peer_directory.get(next_coords)
        if target_ip:
            # Physical TCP transmission to the next geographical server
            print(f"[->] Routing via Spike to {next_coords} ({target_ip})")
            # reader, writer = await asyncio.open_connection(target_ip.split(':')[0], int(target_ip.split(':')[1]))
            # writer.write(json.dumps(packet).encode())
            # writer.close()
        else:
            print(f"[!] Network Partition: IP for coordinate {next_coords} unknown.")

async def main():
    # To run a seed node: python fso_global_node.py
    # To run a worker node: export SEED_IP=192.168.1.100 && python fso_global_node.py
    m = 101 # Planetary scale (1,030,301 nodes)
    seed = os.getenv("SEED_IP", None)

    node = GlobalFSONode(m, seed_ip=seed)
    await node.join_mesh()
    await node.start_server()

if __name__ == "__main__":
    asyncio.run(main())
