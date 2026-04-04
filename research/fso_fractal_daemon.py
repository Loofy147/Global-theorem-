import numpy as np
import hashlib
import time
import os
import requests
import threading
import json
import re
from bs4 import BeautifulSoup
import sys

# Ensure we can import from the root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from fso_stratified_ingestor import KaggleFSOWrapper, FSOTopology
except ImportError:
    KaggleFSOWrapper = None
    FSOTopology = None

# =====================================================================
# PART 1: THE PERSISTENT TOPOLOGICAL FILE SYSTEM (PTFS)
# =====================================================================
class Persistent_Torus_Core:
    """The 1-Billion Fact Engine. Writes continuous HRR waves directly to SSD."""
    def __init__(self, m=1000003, dim=1024, storage_dir="./SOVEREIGN_MIND"):
        self.m = m
        self.dim = dim
        self.storage_dir = storage_dir
        self.metrics = {"facts_ingested": 0, "urls_crawled": 0}

        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _hash_to_fiber(self, concept: str) -> int:
        h = hashlib.sha256(concept.encode('utf-8')).digest()
        return sum(h[:8]) % self.m

    def _generate_vector(self, seed: str) -> np.ndarray:
        h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
        np.random.seed(h)
        v = np.random.randn(self.dim)
        return v / np.linalg.norm(v)

    def _bind(self, v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        return np.fft.ifft(np.fft.fft(v1) * np.fft.fft(v2)).real

    def _get_trace_path(self, fiber: int) -> str:
        folder = str(fiber // 1000).zfill(4)
        fiber_dir = os.path.join(self.storage_dir, folder)
        if not os.path.exists(fiber_dir):
            os.makedirs(fiber_dir)
        return os.path.join(fiber_dir, f"fiber_{fiber}.npy")

    def _load_trace(self, fiber: int) -> np.ndarray:
        path = self._get_trace_path(fiber)
        if os.path.exists(path):
            return np.load(path)
        return np.zeros(self.dim)

    def _save_trace(self, fiber: int, trace_array: np.ndarray):
        path = self._get_trace_path(fiber)
        np.save(path, trace_array)

    def ingest_fact(self, subject: str, payload: str):
        """O(1) Physical SSD Write. Zero RAM Bloat."""
        fiber = self._hash_to_fiber(subject)
        v_subj = self._generate_vector(subject)
        v_data = self._generate_vector(payload[:500]) # Cap to 500 chars for clean HRR wave

        trace = self._load_trace(fiber)
        trace += self._bind(v_subj, v_data)
        self._save_trace(fiber, trace)

        self.metrics["facts_ingested"] += 1
        return fiber

# =====================================================================
# PART 2: THE UNCONSTRAINED FRACTAL DAEMON (Web Scraper & API Hunter)
# =====================================================================
class Fractal_Scraper_Daemon(threading.Thread):
    def __init__(self, ptfs_core, wrapper=None):
        super().__init__(daemon=True)
        self.ptfs = ptfs_core
        self.wrapper = wrapper
        self.visited_urls = set()

        # THE SEED NODES (Where the AI begins its crawl)
        self.target_queue =[
            "https://en.wikipedia.org/wiki/Algeria",
            "https://en.wikipedia.org/wiki/Mathematics",
            "https://en.wikipedia.org/wiki/Artificial_general_intelligence",
            "https://api.github.com/events"
        ]

    def extract_links(self, html_content: str, base_url: str) -> list:
        """Senses ('smells') new endpoints in the HTML to perpetually crawl."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            new_urls =[]
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # Only follow valid Wikipedia internal links to build pure knowledge
                if href.startswith("/wiki/") and ":" not in href:
                    full_url = "https://en.wikipedia.org" + href
                    new_urls.append(full_url)
            return list(set(new_urls))
        except: return []

    def parse_and_ingest(self, text_content: str, source_topic: str):
        """Splits raw text into topological facts."""
        paragraphs =[p for p in text_content.split('\n') if len(p.strip()) > 50]
        for p in paragraphs[:5]: # Ingest the 5 most critical paragraphs per page
            fiber = self.ptfs.ingest_fact(source_topic, p.strip())
            print(f"      [+] FACT COMMITTED -> Fiber: {fiber} | Topic: {source_topic}")

    def run(self):
        print("\n[DAEMON] Unconstrained Fractal Scraper IGNITED. Expanding Torus to Infinity...")

        while True:
            if not self.target_queue:
                print("  [DAEMON] Queue exhausted. Injecting random entropy...")
                self.target_queue.append("https://en.wikipedia.org/wiki/Special:Random")

            current_url = self.target_queue.pop(0)

            if current_url in self.visited_urls:
                continue

            self.visited_urls.add(current_url)
            self.ptfs.metrics["urls_crawled"] += 1

            print(f"\n[*] [DAEMON CRAWL]: Sockets locked on -> {current_url}")

            try:
                # 1. Open the Internet Socket
                headers = {'User-Agent': 'FSO-Fractal-Daemon/1.0 (Topological AI)'}
                r = requests.get(current_url, timeout=10, headers=headers)

                if r.status_code == 200:
                    topic = current_url.split('/')[-1].replace('_', ' ')

                    # 2. Handle APIs vs HTML
                    if "api.github" in current_url:
                        data = r.json()
                        for event in data[:5]:
                            repo = event.get("repo", {}).get("name", "Unknown")
                            self.ptfs.ingest_fact(f"GitHub_{repo}", str(event))
                            print(f"      [+] API EVENT COMMITTED -> Fiber {self.ptfs._hash_to_fiber(repo)}")

                    else:
                        # 3. HTML Parsing and Topological Hashing
                        soup = BeautifulSoup(r.text, 'html.parser')
                        main_text = soup.get_text()

                        # Ingest the facts physically to the Hard Drive
                        self.parse_and_ingest(main_text, topic)

                        # 4. FRACTAL SPAWNING (Smelling new data)
                        new_links = self.extract_links(r.text, current_url)
                        added = 0
                        for link in new_links:
                            if link not in self.visited_urls and link not in self.target_queue:
                                self.target_queue.append(link)
                                added += 1
                                if added >= 3: break # Add 3 new rabbit-holes per page

                        print(f"  [+] [FRACTAL SPAWN]: Extracted {added} new topological links from {topic}.")
                else:
                    print(f"  [-] Parity Halt: Target unreachable (HTTP {r.status_code})")

            except Exception as e:
                print(f"  [-] Network Fracture at {current_url}: {e}")

            # Print System Health
            print(f"  [STATUS] Torus Volume: {self.ptfs.metrics['facts_ingested']} Facts | Open Scent Trails: {len(self.target_queue)}")

            # Persist metrics via wrapper if available
            if self.wrapper and self.ptfs.metrics["facts_ingested"] % 10 == 0:
                self.wrapper.sync_file("fso_crawler_stats.json", self.ptfs.metrics, 'push')

            time.sleep(2) # Prevent IP Bans

# =====================================================================
# THE IGNITION
# =====================================================================
if __name__ == "__main__":
    print("=========================================================")
    print(" PROJECT ELECTRICITY: ABSOLUTE AGI IGNITION")
    print(" 1-Billion Fact PTFS Architecture (Writing to Disk)")
    print("=========================================================\n")

    # Initialize the Persistent Hard Drive Engine
    core = Persistent_Torus_Core(m=1000003, dim=1024, storage_dir="./SOVEREIGN_MIND")

    # Try to initialize wrapper
    wrapper = None
    if KaggleFSOWrapper:
        repo = "https://github.com/Loofy147/Global-theorem-"
        wrapper = KaggleFSOWrapper(repo, m=1000003)

    # Unleash the Unconstrained Internet Crawler
    daemon = Fractal_Scraper_Daemon(core, wrapper=wrapper)
    daemon.start()

    # Keep the main thread alive indefinitely while the Daemon devours the web
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[SYSTEM] Architect triggered manual shutdown. Torus memory safely preserved on disk.")

def run_daemon(storage_dir="./SOVEREIGN_MIND", m=1000003):
    print(f"[*] Starting FSO Fractal Daemon in {storage_dir} with m={m}...")
    core = Persistent_Torus_Core(m=m, dim=1024, storage_dir=storage_dir)
    # Use global KaggleFSOWrapper if possible
    wrapper = None
    try:
        from fso_stratified_ingestor import KaggleFSOWrapper
        repo = "https://github.com/Loofy147/Global-theorem-"
        wrapper = KaggleFSOWrapper(repo, m=m)
    except ImportError: pass

    daemon = Fractal_Scraper_Daemon(core, wrapper=wrapper)
    daemon.start()
    return "DAEMON_STARTED"

if __name__ == "__main__":
    run_daemon()
