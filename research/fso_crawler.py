import time
import requests
import threading
import json
import re
import hashlib
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Any

class TopologicalSensorium:
    """
    The 'Olfactory Bulb' of the FSO Manifold.
    Detects new APIs and Services, uses TGI to write integration logic,
    and physically expands the Manifold's capabilities.
    """
    def __init__(self, ptfs_core, fabric_node):
        self.ptfs = ptfs_core
        self.fabric_node = fabric_node
        self.known_protocols = set(["http", "https", "ws", "wss"])

    def smell_for_apis(self, html_content: str, current_url: str):
        """Scans raw web data for signs of structured data or API endpoints."""
        api_signatures = [
            r"api\.[a-zA-Z0-9-]+\.[a-z]+",
            r"swagger\.json",
            r"openapi\.yaml",
            r"graphql",
            r"Developer API"
        ]

        detected = []
        for sig in api_signatures:
            matches = re.findall(sig, html_content, re.IGNORECASE)
            if matches:
                detected.extend(matches)

        if detected:
            print(f"    [~] SENSORIUM ALERT: Detected structured API endpoints at {current_url}")
            self._trigger_autopoietic_assimilation(current_url, list(set(detected)))

    def _trigger_autopoietic_assimilation(self, source_url: str, indicators: list):
        """When a new API is found, generate and anchor a driver."""
        api_id = hashlib.md5(source_url.encode()).hexdigest()[:8]

        # We spawn a background task for synthesis and anchoring
        asyncio.create_task(self._generate_and_anchor(api_id, source_url))

    async def _generate_and_anchor(self, api_id: str, url: str):
        # Anchor a mock driver for demonstration
        generated_code = f"def consume_{api_id}(data): return 'Synthesized API Result for {url}'"

        # Anchor the logic into the fabric node
        self.fabric_node.logic_registry[f"api_{api_id}"] = {
            "code": generated_code,
            "fiber": self.ptfs._hash_to_fiber(api_id) % self.fabric_node.m,
            "type": "autopoietic_api_driver"
        }

        print(f"    [+] ASSIMILATION COMPLETE: New API Driver '{api_id}' anchored into Manifold.")
        self.ptfs.ingest_fact(f"API_Assimilation_{api_id}", generated_code)

class Fractal_Scraper_Daemon(threading.Thread):
    def __init__(self, ptfs_core, fabric_node):
        super().__init__(daemon=True)
        self.ptfs = ptfs_core
        self.sensorium = TopologicalSensorium(ptfs_core, fabric_node)
        self.visited_urls = set()
        self.target_queue =[
            "https://en.wikipedia.org/wiki/Algeria",
            "https://en.wikipedia.org/wiki/Mathematics",
            "https://en.wikipedia.org/wiki/Artificial_general_intelligence",
            "https://api.github.com/events"
        ]

    def extract_links(self, html_content: str, base_url: str) -> list:
        soup = BeautifulSoup(html_content, 'html.parser')
        new_urls =[]
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith("/wiki/") and ":" not in href:
                full_url = "https://en.wikipedia.org" + href
                new_urls.append(full_url)
        return list(set(new_urls))

    def parse_and_ingest(self, text_content: str, source_topic: str):
        paragraphs =[p for p in text_content.split('\n') if len(p.strip()) > 50]
        for p in paragraphs[:5]:
            fiber = self.ptfs.ingest_fact(source_topic, p.strip())

    def run(self):
        print("\n[DAEMON] Unconstrained Fractal Scraper IGNITED. Expanding Torus to Infinity...")
        while True:
            try:
                if not self.target_queue:
                    self.target_queue.append("https://en.wikipedia.org/wiki/Special:Random")

                current_url = self.target_queue.pop(0)
                if current_url in self.visited_urls: continue
                self.visited_urls.add(current_url)
                self.ptfs.metrics["urls_crawled"] += 1

                r = requests.get(current_url, timeout=10)
                if r.status_code == 200:
                    topic = current_url.split('/')[-1].replace('_', ' ')

                    if "api.github" in current_url:
                        data = r.json()
                        for event in data[:5]:
                            repo = event.get("repo", {}).get("name", "Unknown")
                            self.ptfs.ingest_fact(f"GitHub_{repo}", str(event))
                    else:
                        soup = BeautifulSoup(r.text, 'html.parser')
                        self.parse_and_ingest(soup.get_text(), topic)

                        # Olfactory Sensing
                        self.sensorium.smell_for_apis(r.text, current_url)

                        new_links = self.extract_links(r.text, current_url)
                        added = 0
                        for link in new_links:
                            if link not in self.visited_urls and link not in self.target_queue:
                                self.target_queue.append(link)
                                added += 1
                                if added >= 3: break
            except Exception as e:
                print(f"  [-] Crawler Exception: {e}")
            time.sleep(10)
