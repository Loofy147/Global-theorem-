import asyncio
import hashlib
import json
import socket
import uuid
import os
import sys
import ipaddress
from typing import Tuple, Dict, List, Any
from aiohttp import web

# Add parent directory to path for core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research.fso_fabric import FSOFabricNode

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
    TRUSTED_BACKBONE_RANGES = [
        ipaddress.ip_network("74.220.48.0/24"),
        ipaddress.ip_network("74.220.56.0/24")
    ]

    def __init__(self, m: int, seed_ip: str = None):
        self.m = m
        self.topo = FSOTopology(m)
        self.node_id = str(uuid.uuid4())
        self.public_ip = self._get_public_ip()

        # Priority: PORT (Render/HF) -> FSO_PORT -> Default 10000
        self.port = int(os.getenv("PORT", os.getenv("FSO_PORT", 10000)))

        self.coords = None
        self.fiber = None
        self.fabric_node: FSOFabricNode = None
        self.peer_directory: Dict[Tuple[int,int,int], str] = {}
        self.seed_ip = seed_ip

    def _get_public_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def is_trusted_peer(self, ip_str: str) -> bool:
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            return any(ip_obj in network for network in self.TRUSTED_BACKBONE_RANGES)
        except ValueError:
            return False

    async def join_mesh(self):
        print(f"[*] Booting Global Node {self.node_id} at {self.public_ip}:{self.port}")
        if self.seed_ip:
            h = int(hashlib.md5(self.public_ip.encode()).hexdigest(), 16)
            self.coords = (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)
        else:
            self.coords = (0, 0, 0)
        self.fiber = sum(self.coords) % self.m
        self.fabric_node = FSOFabricNode(self.coords, self.m)
        print(f"[+] Successfully integrated into FSO Manifold at {self.coords} (Fiber {self.fiber})")

    async def handle_health(self, request):
        return web.Response(text=json.dumps({"status": "UP", "node_id": self.node_id, "coords": self.coords}), content_type='application/json')

    async def handle_wave_http(self, request):
        try:
            packet = await request.json()
            result = await self.fabric_node.process_waveform(packet)
            return web.Response(text=json.dumps(result), content_type='application/json')
        except Exception as e:
            return web.Response(text=json.dumps({"status": "ERROR", "error": str(e)}), status=400)

    async def start_server(self):
        app = web.Application()
        app.add_routes([
            web.get('/', self.handle_health),
            web.get('/health', self.handle_health),
            web.post('/wave', self.handle_wave_http)
        ])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        print(f"[+] FSO Global Node Listening on 0.0.0.0:{self.port} (HTTP)")
        await site.start()
        # Keep alive
        while True:
            await asyncio.sleep(3600)

async def main():
    m = 101
    seed = os.getenv("SEED_IP", None)
    node = GlobalFSONode(m, seed_ip=seed)
    await node.join_mesh()
    await node.start_server()

if __name__ == "__main__":
    asyncio.run(main())
