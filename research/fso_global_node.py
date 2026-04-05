import asyncio
import hashlib
import json
import socket
import uuid
import os
import sys
import ipaddress
import aiohttp
import time
from aiohttp import web
from typing import Tuple, Dict, List, Any
from datetime import datetime

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
        self.port = int(os.getenv("PORT", os.getenv("FSO_PORT", 8888)))

        self.coords = None
        self.fiber = None
        self.fabric_node: FSOFabricNode = None
        self.peer_directory: Dict[Tuple[int,int,int], str] = {}

        self.seed_ip = seed_ip

        # Autonomous Telemetry
        self.auto_stats = {
            "last_heal": "Never",
            "last_synthesis": "Never",
            "tasks_processed": 0,
            "status": "BOOTING"
        }

        # Load dashboard HTML
        self.dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
        self.dashboard_html = "<h1>Dashboard Load Error</h1>"
        if os.path.exists(self.dashboard_path):
            with open(self.dashboard_path, "r") as f:
                self.dashboard_html = f.read()

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

    def is_trusted_peer(self, ip_str: str) -> bool:
        """Verifies if an incoming IP belongs to the trusted backbone (Render)."""
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            return any(ip_obj in network for network in self.TRUSTED_BACKBONE_RANGES)
        except ValueError:
            return False

    async def join_mesh(self):
        """Contacts the seed node to claim an (x,y,z) coordinate in the Torus."""
        print(f"[*] Booting Global Node {self.node_id} at {self.public_ip}:{self.port}")

        if self.seed_ip:
            h = int(hashlib.md5(self.public_ip.encode()).hexdigest(), 16)
            self.coords = (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)
        else:
            self.coords = (0, 0, 0)

        self.fiber = sum(self.coords) % self.m

        # Initialize the FSO Cognitive Core for this physical node
        self.fabric_node = FSOFabricNode(self.coords, self.m)

        print(f"[+] Successfully integrated into FSO Manifold at {self.coords} (Fiber {self.fiber})")
        self.auto_stats["status"] = "AUTONOMOUS_RUNNING"

    async def handle_health(self, request):
        """Health check endpoint for Render."""
        return web.Response(text="FSO Node Active", status=200)

    async def handle_dashboard(self, request):
        """Serves the FSO Planetary Admin Dashboard."""
        return web.Response(text=self.dashboard_html, content_type='text/html')

    async def handle_telemetry(self, request):
        """Provides live manifold telemetry for the dashboard."""
        manifest_path = os.path.join(os.path.dirname(__file__), "fso_production_manifest.json")
        units_count = 0
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r") as f:
                    units_count = len(json.load(f))
            except: pass

        return web.json_response({
            "nodes": self.m**3,
            "logic_units": units_count or len(self.fabric_node.logic_registry),
            "fiber": self.fiber,
            "coords": self.coords,
            "auto_stats": self.auto_stats
        })

    async def handle_command_api(self, request):
        """Processes high-level dashboard commands with input validation."""
        try:
            data = await request.json()
            concept = data.get("concept")
            token = data.get("token")

            if not token or "ADMIN" not in token:
                return web.json_response({"status": "UNAUTHORIZED"}, status=401)

            valid_concepts = ["sync", "heal", "smelt"]
            if not concept or concept not in valid_concepts:
                return web.json_response({"status": "INVALID_COMMAND", "valid_options": valid_concepts}, status=400)

            print(f"[DASHBOARD] Mapping Concept '{concept}' to Hamiltonian Logic...")
            result = None
            if concept == "sync":
                result = await self.fabric_node.process_waveform({
                    "color": 2, "type": "SYNC_CALIBRATION", "payload": {"fiber": self.fiber}
                })
            elif concept == "smelt":
                result = await self.fabric_node.process_waveform({
                    "color": 0, "type": "LOGIC_INJECT", "payload": {"id": "refinery_task", "code": "smelt_repo()"}
                })
                self.auto_stats["last_synthesis"] = datetime.now().isoformat()
            elif concept == "heal":
                result = await self.fabric_node.process_waveform({
                    "color": 2, "type": "RESILIENCE_HEAL", "payload": {"target_fiber": self.fiber}
                })
                self.auto_stats["last_heal"] = datetime.now().isoformat()

            return web.json_response(result or {"status": "WAVE_PROPAGATED"})
        except Exception as e:
            return web.json_response({"status": "ERROR", "reason": str(e)}, status=500)

    async def handle_wave_http(self, request):
        """Processes incoming Hamiltonian waves via HTTP POST."""
        client_ip = request.remote
        try:
            packet = await request.json()
            color = packet.get("color")
            trusted = self.is_trusted_peer(client_ip)
            trust_marker = "[TRUSTED]" if trusted else "[EXTERNAL]"
            print(f"{trust_marker} Received Color {color} Wave from {client_ip}")

            result = await self.fabric_node.process_waveform(packet)
            self.auto_stats["tasks_processed"] += 1

            target_coords = tuple(packet.get('target', (0,0,0)))
            if target_coords != self.coords and packet.get('ttl', 0) > 0:
                packet['ttl'] -= 1
                next_coords = self.topo.spike_step(self.coords, color)
                asyncio.create_task(self._physical_forward(next_coords, packet))

            return web.json_response(result or {"status": "PROCESSED"})
        except Exception as e:
            print(f"[!] Error processing wave from {client_ip}: {e}")
            return web.Response(text=str(e), status=400)

    async def start_autonomous_loop(self):
        """Periodic background tasks for manifold health and expansion."""
        print("[*] Initiating Autonomous Governance Loop...")
        while True:
            try:
                # 1. Periodic Healing (Color 2)
                await self.fabric_node.process_waveform({
                    "color": 2, "type": "RESILIENCE_HEAL", "payload": {"target_fiber": self.fiber}
                })
                self.auto_stats["last_heal"] = datetime.now().isoformat()

                # 2. Random Synthesis (Autopoietic Expansion)
                if time.time() % 3600 < 300: # Every hour, 5 min window for synthesis
                    print("[AUTOP] Background synthesis triggered...")
                    # Mocking synthesis intent
                    await self.fabric_node.process_waveform({
                        "color": 0, "type": "LOGIC_INJECT", "payload": {"id": f"auto_{int(time.time())}", "code": "def auto_logic(): pass"}
                    })
                    self.auto_stats["last_synthesis"] = datetime.now().isoformat()

                # 3. Manifold Snapshot (Simulated)
                # print(f"[SYS] Autonomous Heartbeat: Fiber {self.fiber} is STABLE.")

            except Exception as e:
                print(f"[!] Autonomous loop error: {e}")

            await asyncio.sleep(300) # Run every 5 minutes

    async def start_server(self):
        """Starts the aiohttp server for FSO wave processing and dashboard."""
        app = web.Application()
        app.add_routes([
            web.get('/', self.handle_health),
            web.get('/dashboard', self.handle_dashboard),
            web.get('/api/telemetry', self.handle_telemetry),
            web.post('/api/command', self.handle_command_api),
            web.post('/wave', self.handle_wave_http),
            web.post('/', self.handle_wave_http)
        ])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        print(f"[+] FSO HTTP Server with Dashboard listening on 0.0.0.0:{self.port}")

        # Start Autonomous Loop in background
        asyncio.create_task(self.start_autonomous_loop())

        await site.start()
        # Keep running
        while True:
            await asyncio.sleep(3600)

    async def _physical_forward(self, next_coords, packet):
        """Resolves (x,y,z) to an IP and forwards the wave via HTTP POST."""
        target_ip = self.peer_directory.get(next_coords)
        if target_ip:
            print(f"[->] Routing via Spike to {next_coords} ({target_ip})")
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"http://{target_ip}/wave"
                    async with session.post(url, json=packet, timeout=5) as resp:
                        return await resp.json()
            except Exception as e:
                print(f"[!] Forwarding failed to {next_coords}: {e}")
        else:
            print(f"[!] Network Partition: IP for {next_coords} unknown. Packet dropped.")

async def main():
    m = 101 # Planetary scale
    seed = os.getenv("SEED_IP", None)

    node = GlobalFSONode(m, seed_ip=seed)
    await node.join_mesh()
    await node.start_server()

if __name__ == "__main__":
    asyncio.run(main())
