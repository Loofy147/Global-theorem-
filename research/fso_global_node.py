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
import threading
from aiohttp import web
from typing import Tuple, Dict, List, Any
from datetime import datetime
from collections import defaultdict

# Add parent directory to path for core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research.fso_fabric import FSOFabricNode
from research.fso_ptfs import Persistent_Torus_Core
from research.fso_crawler import Fractal_Scraper_Daemon

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
        self.port = int(os.getenv("PORT", 10000))

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
            "status": "BOOTING",
            "facts_ingested": 0,
            "urls_crawled": 0
        }

        # Initialize PTFS and Crawler
        self.ptfs = Persistent_Torus_Core(m=1000003, dim=1024, storage_dir="./SOVEREIGN_MIND")
        self.crawler = None

        # Optimization: Manifest and Logic Cache
        self.manifest_cache = None
        self.prefix_index = defaultdict(dict)
        self.reverse_coords_index = {} # (x,y,z) -> logic_id for O(1) discovery
        self.last_manifest_load = 0

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
        """Initializes the FSO identity and connects to the global Torus."""
        print(f"[*] FSO Node '{self.node_id}' joining Torus (m={self.m})...")

        if self.public_ip:
            h = int(hashlib.sha256(self.public_ip.encode()).hexdigest(), 16)
            self.coords = (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)
        else:
            self.coords = (0, 0, 0)

        self.fiber = sum(self.coords) % self.m

        # Initialize the FSO Cognitive Core for this physical node
        self.fabric_node = FSOFabricNode(self.coords, self.m)

        # Start Crawler Daemon
        self.crawler = Fractal_Scraper_Daemon(self.ptfs, self.fabric_node)
        self.crawler.start()

        print(f"[+] Successfully integrated into FSO Manifold at {self.coords} (Fiber {self.fiber})")
        self.auto_stats["status"] = "AUTONOMOUS_RUNNING"

    def _get_manifest(self):
        """Cached access to the production manifest with O(1) prefix and coordinate indexing."""
        now = time.time()
        if self.manifest_cache is not None and (now - self.last_manifest_load) < 60:
            return self.manifest_cache

        manifest_path = os.path.join(os.path.dirname(__file__), "fso_production_manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r") as f:
                    self.manifest_cache = json.load(f)
                    self.last_manifest_load = now

                    # Rebuild indexes
                    self.prefix_index.clear()
                    self.reverse_coords_index.clear()
                    for logic_id, data in self.manifest_cache.items():
                        # Prefix Index for Bundle Retrieval
                        prefix = logic_id.split('.')[0]
                        code = data.get("code", "") if isinstance(data, dict) else data
                        self.prefix_index[prefix][logic_id] = code

                        # Reverse Coords Index for O(1) Discovery
                        if isinstance(data, dict) and 'coords' in data:
                            c = tuple(data['coords'])
                            self.reverse_coords_index[c] = logic_id
            except:
                self.manifest_cache = {}
        else:
            self.manifest_cache = {}
        return self.manifest_cache

    async def handle_health(self, request):
        """Health check endpoint for Render."""
        return web.Response(text="FSO Node Active", status=200)

    async def handle_dashboard(self, request):
        """Serves the FSO Planetary Admin Dashboard."""
        return web.Response(text=self.dashboard_html, content_type='text/html')

    async def handle_fiber_query(self, request):
        """Dynamic logic bundle retrieval for stratos-os client."""
        if not self.fabric_node:
            return web.json_response({"status": "INITIALIZING"}, status=503)

        lib_target = request.query.get("lib")
        if not lib_target:
            return web.json_response({"status": "ERROR", "reason": "No library specified"}, status=400)

        print(f"[⚡] FIBER QUERY: Reconstituting bundle for '{lib_target}'...")

        logic_bundle = {}
        # Scan local fabric node
        for logic_id, entry in self.fabric_node.logic_registry.items():
            if logic_id.startswith(lib_target):
                logic_bundle[logic_id] = entry.get("code", "")

        # O(1) retrieval from prefix index
        self._get_manifest()
        if lib_target in self.prefix_index:
            logic_bundle.update(self.prefix_index[lib_target])

        return web.json_response({
            "status": "SUCCESS",
            "lib": lib_target,
            "logic_bundle": logic_bundle
        })

    async def handle_telemetry(self, request):
        """Provides live manifold telemetry for the dashboard."""
        if not self.fabric_node:
            return web.json_response({"status": "INITIALIZING"}, status=503)

        manifest = self._get_manifest()
        units_count = len(manifest)

        # Update auto_stats with PTFS metrics
        self.auto_stats["facts_ingested"] = self.ptfs.metrics["facts_ingested"]
        self.auto_stats["urls_crawled"] = self.ptfs.metrics["urls_crawled"]

        return web.json_response({
            "nodes": self.m**3,
            "logic_units": units_count or len(self.fabric_node.logic_registry),
            "fiber": self.fiber,
            "coords": self.coords,
            "auto_stats": self.auto_stats
        })

    async def handle_command_api(self, request):
        """Processes high-level dashboard commands with input validation."""
        if not self.fabric_node:
            return web.json_response({"status": "INITIALIZING"}, status=503)
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
        if not self.fabric_node:
            return web.json_response({"status": "INITIALIZING"}, status=503)
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


    async def gossip_loop(self):
        '''Periodically exchanges peer directories with random nodes.'''
        print('[GOSSIP] Starting Gossip Synchronization Loop...')
        while True:
            await asyncio.sleep(60)
            if not self.peer_directory and not self.seed_ip:
                continue

            # Target selection: seed or random known peer
            targets = []
            if self.seed_ip:
                targets.append(self.seed_ip)

            if self.peer_directory:
                import random
                known_ips = list(self.peer_directory.values())
                targets.extend(random.sample(known_ips, min(len(known_ips), 2)))

            for target_ip in set(targets):
                if target_ip == self.public_ip: continue
                try:
                    async with aiohttp.ClientSession() as session:
                        url = f'http://{target_ip}/api/gossip'
                        payload = {
                            'origin_coords': self.coords,
                            'origin_ip': self.public_ip,
                            'directory': {str(k): v for k, v in self.peer_directory.items()}
                        }
                        async with session.post(url, json=payload, timeout=5) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                self._merge_peers(data.get('directory', {}))
                except Exception as e:
                    print(f'[GOSSIP] Failed to gossip with {target_ip}: {e}')

    async def handle_gossip(self, request):
        '''Endpoint for receiving gossip updates.'''
        try:
            data = await request.json()
            origin_ip = data.get('origin_ip')
            origin_coords = tuple(data.get('origin_coords', (0,0,0)))

            # Register the sender
            if origin_ip and origin_coords:
                self.peer_directory[origin_coords] = origin_ip

            # Merge their known directory
            remote_dir = data.get('directory', {})
            self._merge_peers(remote_dir)

            return web.json_response({
                'status': 'SUCCESS',
                'directory': {str(k): v for k, v in self.peer_directory.items()}
            })
        except Exception as e:
            return web.json_response({'status': 'ERROR', 'reason': str(e)}, status=400)

    def _merge_peers(self, remote_dir):
        '''Merges a remote peer directory into the local state.'''
        import ast
        for coords_str, ip in remote_dir.items():
            try:
                coords = ast.literal_eval(coords_str)
                if coords != self.coords and coords not in self.peer_directory:
                    print(f'[GOSSIP] Discovered new node {coords} at {ip}')
                    self.peer_directory[coords] = ip
            except:
                continue

    async def start_autonomous_loop(self):
        """Periodic background tasks for manifold health and expansion."""
        print("[*] Initiating Autonomous Governance Loop...")
        while True:
            if self.fabric_node:
                try:
                    # 1. Periodic Healing (Color 2)
                    await self.fabric_node.process_waveform({
                        "color": 2, "type": "RESILIENCE_HEAL", "payload": {"target_fiber": self.fiber}
                    })
                    self.auto_stats["last_heal"] = datetime.now().isoformat()

                    # 2. Random Synthesis (Autopoietic Expansion)
                    if time.time() % 3600 < 600:
                        print("[AUTOP] Background synthesis triggered...")
                        await self.fabric_node.process_waveform({
                            "color": 0, "type": "LOGIC_INJECT", "payload": {"id": f"auto_{int(time.time())}", "code": "def auto_logic(): pass"}
                        })
                        self.auto_stats["last_synthesis"] = datetime.now().isoformat()

                except Exception as e:
                    print(f"[!] Autonomous loop error: {e}")

            await asyncio.sleep(300) # Run every 5 minutes

    async def start_server(self):
        """Starts the aiohttp server for FSO wave processing and dashboard."""
        app = web.Application()
        app.add_routes([
            web.get('/', self.handle_dashboard),
            web.get('/dashboard', self.handle_dashboard),
            web.get('/health', self.handle_health),
            web.get('/api/telemetry', self.handle_telemetry),
            web.get('/api/fiber_query', self.handle_fiber_query),
            web.post('/api/gossip', self.handle_gossip),
            web.post('/api/command', self.handle_command_api),
            web.post('/wave', self.handle_wave_http),
            web.post('/', self.handle_wave_http)
        ])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)

        # Start core initialization in background so port can bind immediately
        asyncio.create_task(self.join_mesh())

        print(f"[RENDER] Binding to port {self.port}...")
        await site.start()
        print(f"[RENDER] Port {self.port} active. Service LIVE.")

        asyncio.create_task(self.start_autonomous_loop())
        asyncio.create_task(self.gossip_loop())
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
    m = 101
    seed = os.getenv("SEED_IP", None)
    node = GlobalFSONode(m, seed_ip=seed)
    await node.start_server()

if __name__ == "__main__":
    asyncio.run(main())
