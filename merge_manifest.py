import json
import os

def merge():
    manifest_path = "research/fso_production_manifest.json"
    state_file = "fso_manifold_state.json"

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    with open(state_file, "r") as f:
        state = json.load(f)

    count = 0
    for fid, meta in manifest.items():
        coords = meta.get("coords")
        if coords:
            # Standardize coordinates to "(x, y, z)" string format
            coord_str = f"({coords[0]}, {coords[1]}, {coords[2]})"
            state["registry"][coord_str] = fid
            count += 1

    with open(state_file, "w") as f:
        json.dump(state, f, indent=4)

    print(f"[*] Standardized and merged {count} units from manifest.")

if __name__ == "__main__":
    merge()
