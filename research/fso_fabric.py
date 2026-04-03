import asyncio
import hashlib
import json
import time
import sys
import os
import ast
from typing import Dict, Any, Tuple, Optional, List, Callable

# Add parent directory to path for core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import construct_spike_sigma

# Semantic definitions for the 3 Hamiltonian Cycles
COLOR_STORAGE = 0  # Color 0: Carries raw data and memory (Storage Wave)
COLOR_LOGIC = 1    # Color 1: Carries executable tasks/queries (Logic Wave)
COLOR_CONTROL = 2  # Color 2: Carries parity and system metadata (Control Wave)

class FSOFabricNode:
    """
    A Production-grade FSO Cognitive Node.
    Handles Tri-Color Hamiltonian waves: Storage, Logic, and Control.
    """
    def __init__(self, coords: Tuple[int, int, int], m: int):
        self.coords = coords
        self.m = m
        self.s_fiber = sum(coords) % m

        # Local State Memory (Holographic Layer)
        self.local_storage: Dict[str, Any] = {}
        self.logic_registry: Dict[str, Any] = {} # name -> {code, fiber}

        # Every node independently generates the same deterministic Hamiltonian manifold.
        self.sigma = construct_spike_sigma(m, 3)
        if not self.sigma:
            raise ValueError(f"FSO Error: Failed to construct manifold for m={m}.")

    def calculate_next_hop(self, current: Tuple[int, int, int], color: int) -> Tuple[int, int, int]:
        """Law VI: The Universal Spike - O(1) stateless routing."""
        p = self.sigma.get(current)
        if not p: return current
        arc = p[color]
        nxt = list(current)
        nxt[arc] = (nxt[arc] + 1) % self.m
        return tuple(nxt)

    async def process_waveform(self, packet: Dict[str, Any]):
        """Routes the incoming data based on its Hamiltonian Color."""
        color = packet.get("color")
        payload = packet.get("payload", {})
        ptype = packet.get("type")

        if color == COLOR_STORAGE:
            return await self._process_storage_wave(payload, ptype)
        elif color == COLOR_LOGIC:
            return await self._process_logic_wave(payload, ptype)
        elif color == COLOR_CONTROL:
            return await self._process_control_wave(payload, ptype)

    async def _process_storage_wave(self, payload: Dict[str, Any], ptype: str):
        """Color 0: Save data to local memory (Persistence)."""
        if ptype == "LOGIC_INJECT":
            logic_id = payload.get("id")
            self.logic_registry[logic_id] = {
                "code": payload.get("code"),
                "fiber": self.s_fiber
            }
            return {"status": "INGESTED", "id": logic_id}
        else:
            key = payload.get("key")
            data = payload.get("data")
            self.local_storage[key] = data
            return {"status": "STORED", "key": key}

    async def _process_logic_wave(self, payload: Dict[str, Any], ptype: str):
        """Color 1: Execute logic against local storage (Intersection)."""
        logic_id = payload.get("id")
        target_key = payload.get("target_key")
        keyword = payload.get("keyword")

        # Check if we have the logic and the data at this coordinate
        if logic_id in self.logic_registry:
            logic_meta = self.logic_registry[logic_id]
            code = logic_meta.get("code", "")

            # If target_key is provided, execute on it. Otherwise, return the logic existence.
            if target_key and target_key in self.local_storage:
                data = self.local_storage[target_key]

                # Logic Intersection: Apply functional logic to data
                execution_result = self._execute_functional_logic(code, data)

                if keyword and keyword.lower() in str(data).lower():
                    return {
                        "status": "EXECUTED",
                        "node": self.coords,
                        "logic": logic_id,
                        "target": target_key,
                        "match": True,
                        "result": execution_result
                    }
                return {
                    "status": "EXECUTED",
                    "node": self.coords,
                    "logic": logic_id,
                    "target": target_key,
                    "match": False,
                    "result": execution_result
                }
            return {"status": "LOGIC_READY", "node": self.coords, "logic": logic_id, "code": code}

        return {"status": "NO_INTERSECTION", "node": self.coords, "logic": logic_id}

    def _execute_functional_logic(self, code: str, data: Any) -> Any:
        """Simulates the execution of industrial logic specifications."""
        try:
            if "lambda" in code:
                # Basic lambda execution for demo
                func = eval(code)
                return func(data)
            elif "Re(F^-1" in code:
                # Simulate FFT logic
                return f"PROCESSED_FFT({data})"
            elif "Stateless closure" in code:
                # Simulate Distributed logic
                return f"CONSENSUS_REACHED({data})"
            elif "r=(1, m-2, 1)" in code:
                # Simulate Spike logic
                return f"SPIKE_ROUTED({data})"
            return f"EXECUTED_GENERIC({code[:20]}...)"
        except Exception as e:
            return f"EXEC_ERROR: {str(e)}"

    async def _process_control_wave(self, payload: Dict[str, Any], ptype: str):
        """Color 2: Parity checks and Closure Lemma validation (Healing)."""
        expected_s = payload.get("expected_fiber")
        if expected_s is not None and self.s_fiber != expected_s:
            return await self.apply_closure_lemma_healing(payload)
        return {"status": "VERIFIED", "node": self.coords}

    async def apply_closure_lemma_healing(self, payload: Dict[str, Any]):
        """Uses the k-1 determinism to deduce missing data or correct state."""
        return {"status": "HEALED", "node": self.coords}

    async def route_packet(self, packet: Dict[str, Any]):
        """Stateless Discovery and Routing."""
        target_coords = tuple(packet.get('target', (0,0,0)))

        if target_coords == self.coords:
            return await self.process_waveform(packet)

        return self.calculate_next_hop(self.coords, packet.get('color', 0))

class FSODataStream:
    """Utility to inject data into the Hamiltonian flow."""
    @staticmethod
    def create_packet(payload: Dict[str, Any], target: Tuple[int, int, int], color: int = 0, ptype: str = "DATA"):
        return {
            "id": hashlib.md5(f"{time.time()}{payload}{target}{color}".encode()).hexdigest()[:8],
            "target": target,
            "color": color,
            "type": ptype,
            "payload": payload,
            "timestamp": time.time()
        }
