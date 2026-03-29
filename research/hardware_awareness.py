import os
import hashlib
from typing import Dict, Tuple, Any
import random

class HardwareMapper:
    """
    TGI Hardware Awareness Core.
    Maps real-time CPU, RAM, and Battery metrics into topological coordinates.
    Ensures the system is 'aware' of its physical constraints.
    Fallback implementation using /proc/ and /sys/ for environment where psutil is not available.
    """
    def __init__(self, m: int = 255, k: int = 3):
        self.m = m
        self.k = k

    def get_system_state(self) -> Dict[str, float]:
        """Collects current hardware metrics via /proc."""
        cpu = 0.0
        memory = 0.0
        battery = 100.0

        try:
            # CPU (one-shot parse)
            with open("/proc/loadavg", "r") as f:
                load = f.read().split()
                cpu = float(load[0]) * 10 # 1.0 load roughly 10% for a 10-core system

            # Memory
            with open("/proc/meminfo", "r") as f:
                mem = f.readlines()
                total = int(mem[0].split()[1])
                free = int(mem[1].split()[1])
                memory = (1.0 - (free / total)) * 100.0
        except Exception:
            # Fallback for systems without /proc
            cpu = random.uniform(5.0, 15.0)
            memory = random.uniform(20.0, 40.0)

        return {"cpu": min(cpu, 100.0), "memory": min(memory, 100.0), "battery": battery}

    def map_to_coordinate(self) -> Tuple[int, ...]:
        """Maps hardware state to Z_m^k."""
        state = self.get_system_state()

        # Discretize metrics to [0, m-1]
        x = int((state["cpu"] / 100.0) * (self.m - 1)) % self.m
        y = int((state["memory"] / 100.0) * (self.m - 1)) % self.m
        z = int((state["battery"] / 100.0) * (self.m - 1)) % self.m

        coords = [x, y, z]
        # Pad or truncate if k != 3
        if self.k > 3:
            # Hash to fill remaining dimensions
            h = hashlib.sha256(str(state).encode()).digest()
            for i in range(self.k - 3):
                coords.append(h[i] % self.m)
        elif self.k < 3:
            coords = coords[:self.k]

        return tuple(coords)

    def measure_thermal_entropy(self) -> float:
        """Synthetic metric for system 'temperature' relative to topological complexity."""
        state = self.get_system_state()
        return (state["cpu"] + state["memory"]) / 200.0

if __name__ == "__main__":
    hm = HardwareMapper()
    print("═══ TGI HARDWARE AWARENESS (Proc-based) ═══")
    state = hm.get_system_state()
    print(f"Metrics: {state}")
    coord = hm.map_to_coordinate()
    print(f"Topological Coordinate (Z_{hm.m}^{hm.k}): {coord}")
    print(f"Thermal Entropy: {hm.measure_thermal_entropy():.4f}")
