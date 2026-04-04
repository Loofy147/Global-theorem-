import sys
import os
import time
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.fso_fractal_daemon import Persistent_Torus_Core, Fractal_Scraper_Daemon

def test_fractal_crawl_local():
    print("--- STARTING LOCAL FRACTAL CRAWL VERIFICATION ---")

    # 1. Initialize PTFS locally
    storage = "./TEST_SOVEREIGN_MIND"
    core = Persistent_Torus_Core(m=1000, dim=128, storage_dir=storage)

    # 2. Test direct ingestion
    fiber = core.ingest_fact("TestTopic", "This is a test fact for the absolute recall verification.")
    print(f"Ingested to fiber: {fiber}")
    assert os.path.exists(core._get_trace_path(fiber))

    # 3. Test link extraction (mocking HTML)
    daemon = Fractal_Scraper_Daemon(core)
    html = '<html><body><a href="/wiki/Algeria">Algeria</a><a href="https://api.github.com/events">API</a></body></html>'
    links = daemon.extract_links(html, "https://en.wikipedia.org")
    print(f"Extracted links: {links}")
    assert "https://en.wikipedia.org/wiki/Algeria" in links

    print("[SUCCESS] Fractal Crawl Verification Passed.")

if __name__ == "__main__":
    try:
        test_fractal_crawl_local()
    finally:
        # Cleanup
        import shutil
        if os.path.exists("./TEST_SOVEREIGN_MIND"):
            shutil.rmtree("./TEST_SOVEREIGN_MIND")
