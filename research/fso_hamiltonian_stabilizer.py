import numpy as np
import time
from tgi_calculus_engine import TGICalculusEngine
from tgi_cleanup_gate import TopologicalCleanUpGate

class HamiltonianStabilizer:
    def __init__(self, dim=1024):
        self.dim = dim
        self.engine = TGICalculusEngine(dim=dim)
        self.cleanup = TopologicalCleanUpGate(dim=dim)
        self.manifold_state = np.random.normal(0, 0.01, dim) # Start with noise
        self.targets = []

    def add_environment_target(self, x, y):
        self.targets.append((x, y))
        self.cleanup.register(y, f"env_target_{len(self.targets)}")

    def calculate_hamiltonian(self, state):
        if not self.targets: return 0.0
        total_error = 0.0
        for x, y in self.targets:
            # Query the manifold state for this key
            y_pred = self.engine.bind(state, x)
            # Compare with clean target
            total_error += (1.0 - self.engine.cosine_sim(y_pred, y))
        return total_error / len(self.targets)

    def stabilized_breeding(self, psi_1, psi_2, alpha=0.5):
        psi_child = self.engine.bind(psi_1, psi_2)
        norm = np.linalg.norm(psi_child)
        if norm > 1e-9: psi_child /= norm

        h_old = self.calculate_hamiltonian(self.manifold_state)

        test_state = self.manifold_state + alpha * psi_child
        h_new = self.calculate_hamiltonian(test_state)

        if h_new < h_old:
            self.manifold_state = test_state
            return True, h_new
        return False, h_old

if __name__ == "__main__":
    dim = 1024
    stabilizer = HamiltonianStabilizer(dim=dim)
    engine = stabilizer.engine

    print("--- TGI: HAMILTONIAN STABILIZATION TEST ---")

    # 1. Setup Environment
    env_keys = [engine.generate_unitary() for _ in range(3)]
    env_vals = [engine.generate_unitary() for _ in range(3)]
    for x, y in zip(env_keys, env_vals):
        stabilizer.add_environment_target(x, y)

    initial_h = stabilizer.calculate_hamiltonian(stabilizer.manifold_state)
    print(f"Initial Hamiltonian Energy: {initial_h:.6f}")

    # 2. Simulated 'Breeding' - Proposing perfect logic gates mixed with noise
    success_count = 0
    for i in range(3):
        # Propose a perfect logic gate for target i
        perfect_gate = engine.unbind(env_vals[i], env_keys[i])

        accepted, h = stabilizer.stabilized_breeding(perfect_gate, np.ones(dim))
        if accepted: success_count += 1

    # Propose noise
    for i in range(10):
        noise = np.random.randn(dim)
        accepted, h = stabilizer.stabilized_breeding(noise, noise)
        if accepted: success_count += 1

    final_h = stabilizer.calculate_hamiltonian(stabilizer.manifold_state)
    print(f"Final Hamiltonian Energy: {final_h:.6f}")
    print(f"Accepted {success_count} mutations.")

    if final_h < initial_h:
        print("[SUCCESS] Hamiltonian Minimization drove the system towards logical order.")
    else:
        print("[FAILURE] Energy did not decrease.")
