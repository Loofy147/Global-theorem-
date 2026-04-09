import time
from STRATOS_HARVESTER import StratosHarvester
import os
import shutil

def bench_harvest():
    if os.path.exists("./STRATOS_MEMORY_V2"):
        shutil.rmtree("./STRATOS_MEMORY_V2")
    harvester = StratosHarvester(targets=["json"])
    start = time.perf_counter()
    harvester.harvest_library("json")
    end = time.perf_counter()
    print(f"Harvest 'json' (8 items) time: {end - start:.4f}s")

    # Try something bigger if possible
    harvester = StratosHarvester(targets=["math"])
    start = time.perf_counter()
    harvester.harvest_library("math")
    end = time.perf_counter()
    print(f"Harvest 'math' (56 items) time: {end - start:.4f}s")

if __name__ == "__main__":
    bench_harvest()
