import time
import asyncio
import hashlib
import logging
import os
import sys
from typing import Tuple, Dict, Any

# Configure logging
logger = logging.getLogger("EVOLUTION")

# Try to import GenerativeGate for synthesis
try:
    # Add parent directory to path to ensure relative imports work if needed
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from research.fso_generative_mcp import GenerativeGate
except ImportError:
    GenerativeGate = None
    logger.warning("GenerativeGate not found. Synthesis will be disabled.")

class TopologicalGravity:
    """
    Calculates the 'Pull' between interacting nodes.
    Frequently interacting nodes will drift closer together in the manifold.
    """
    def __init__(self, m: int):
        self.m = m

    def calculate_distance(self, p1: Tuple[int,int,int], p2: Tuple[int,int,int]) -> int:
        """Calculates Toroidal distance (wrapping around edges)."""
        return sum(min(abs(a - b), self.m - abs(a - b)) for a, b in zip(p1, p2))

    def calculate_drift(self, logic_coords: Tuple[int,int,int], caller_coords: Tuple[int,int,int]) -> Tuple[int,int,int]:
        """Moves the logic 1 step closer to the caller to minimize future routing hops."""
        new_coords = list(logic_coords)
        for i in range(3):
            # Move dimension i towards the caller if not already aligned
            if logic_coords[i] != caller_coords[i]:
                dist_direct = (caller_coords[i] - logic_coords[i]) % self.m
                dist_wrap = (logic_coords[i] - caller_coords[i]) % self.m
                
                if dist_direct <= dist_wrap:
                    new_coords[i] = (new_coords[i] + 1) % self.m
                else:
                    new_coords[i] = (new_coords[i] - 1) % self.m
                break # Only drift one spatial dimension at a time
        return tuple(new_coords)

class FSO_Evolution_Engine:
    """
    The Evolutionary Loop:
    1. Measure Execution Time
    2. Rewrite for Speed (LLM/TGI)
    3. Migrate coordinates (Topological Gravity)
    """
    def __init__(self, hypervisor):
        self.apex = hypervisor
        self.m = hypervisor.m
        self.gravity = TopologicalGravity(self.m)
        self.performance_metrics: Dict[str, list] = {} # Tracks execution speeds
        self.gate = None
        if GenerativeGate:
            try:
                self.gate = GenerativeGate(model_id="gpt2")
            except Exception as e:
                logger.error(f"Failed to initialize GenerativeGate: {e}")

    async def consume_knowledge(self, topic: str):
        """Autonomously searches PyPI/GitHub for libraries related to the topic."""
        logger.info(f"Consuming ecosystem knowledge for '{topic}'...")
        # The TGI (LLM) decides what pip library is best.
        # (Simulated TGI decision using logic if LLM is unavailable or for simple mapping)
        best_library = "scipy" if "pixel" in topic or "scientific" in topic else "numpy"
        logger.info(f"TGI Decision: {best_library} is the optimal substrate.")
        self.apex.consumer.auto_provision(best_library)

    async def evaluate_and_evolve(self, logic_id: str, caller_coords: Tuple[int,int,int], *args, **kwargs):
        """
        Executes a logic block, times it, and triggers evolution if it's too slow.
        """
        # Resolve current coords (might have drifted)
        current_coords = self.apex.consumer.logic_to_coords.get(logic_id)
        if not current_coords:
            current_coords = self.apex.topo.get_coords(logic_id)
        
        # 1. Profile the Execution
        start_time = time.perf_counter()
        result = self.apex.consumer.execute_at_coords(current_coords, *args, **kwargs)
        exec_time = time.perf_counter() - start_time
        
        # Track history
        if logic_id not in self.performance_metrics:
            self.performance_metrics[logic_id] = []
        self.performance_metrics[logic_id].append(exec_time)
        
        avg_time = sum(self.performance_metrics[logic_id]) / len(self.performance_metrics[logic_id])
        logger.info(f"'{logic_id}' executed in {exec_time:.5f}s (Avg: {avg_time:.5f}s)")

        # 2. Trigger Topological Gravity
        dist = self.gravity.calculate_distance(current_coords, caller_coords)
        if dist > 1: # If the logic is far from the data
            new_anchor = self.gravity.calculate_drift(current_coords, caller_coords)
            logger.info(f"TOPOLOGICAL DRIFT: Moving '{logic_id}' from {current_coords} to {new_anchor}")
            # Overwrite the hash-based coordinate with an evolved physical coordinate
            if current_coords in self.apex.consumer.global_registry:
                logic_name = self.apex.consumer.global_registry.pop(current_coords)
                self.apex.consumer.global_registry[new_anchor] = logic_name
                self.apex.consumer.logic_to_coords[logic_name] = new_anchor
            
        # 3. Trigger TGI Synthesis (If the code itself is slow)
        if avg_time > 1.0 and self.gate: # Arbitrary threshold for "Too Slow"
            logger.warning(f"BOTTLENECK DETECTED. Triggering Generative Synthesis to rewrite '{logic_id}'...")
            try:
                # Ask the gate to synthesize a faster version
                new_code = await self.gate.synthesize_logic(f"Optimized version of {logic_id} for performance")
                logger.info(f"Synthesized new logic for {logic_id}:\n{new_code}")
                # In production, this would be compiled and hot-swapped
            except Exception as e:
                logger.error(f"Synthesis failed: {e}")
            
        return result
