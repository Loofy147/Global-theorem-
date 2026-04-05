import json
import os

def monitor_holographic_state():
    state_file = "fso_holographic_state.json"
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            state = json.load(f)
            print(f"--- HOLOGRAPHIC RECOVERY MONITOR ---")
            print(f"Status: {state['status']}")
            print(f"Fiber Count: {state['fiber_count']}")
            print(f"Average Integrity: {state['average_integrity']:.10f}")
            print(f"Timestamp: {state['timestamp']}")
    else:
        print("Holographic state not found.")

if __name__ == "__main__":
    monitor_holographic_state()
