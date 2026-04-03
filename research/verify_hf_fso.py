import os
import sys
import json
import asyncio

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from fso_fabric import FSOFabricNode, FSODataStream, COLOR_LOGIC

async def verify_hf_fso():
    print("[*] Starting FSO Hugging Face Verification...")
    m_val = 31

    # Load manifest to get coordinates
    manifest_path = os.path.join(os.path.dirname(__file__), "fso_production_manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # 1. Verify 'transformers.pipeline'
    hf_spec = "transformers.pipeline"
    if hf_spec not in manifest:
        print(f"[!] Error: {hf_spec} not in manifest.")
        return

    coords = tuple(manifest[hf_spec]["coords"])
    print(f"[*] Logic '{hf_spec}' anchored at {coords}")

    # Initialize the node at that coordinate
    node = FSOFabricNode(coords, m_val)

    # Prepare a sentiment analysis task
    payload = {
        "call_spec": hf_spec,
        "data": {
            "task": "sentiment-analysis",
            "model": "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
        }
    }

    packet = FSODataStream.create_packet(payload, coords, color=COLOR_LOGIC)

    print(f"[*] Dispatching Logic Wave to {coords} for sentiment analysis...")
    response = await node.route_packet(packet)

    if response["status"] == "EXECUTED":
        print(f"[+] Success! Result type: {type(response['result'])}")
        pipe = response["result"]
        test_text = "FSO Hamiltonian routing is incredibly efficient!"
        sentiment = pipe(test_text)
        print(f"[+] Sentiment Analysis Result for '{test_text}':")
        print(f"    {sentiment}")
    else:
        print(f"[!] Execution failed: {response}")

    # 2. Verify 'datasets.load_dataset'
    ds_spec = "datasets.load_dataset"
    if ds_spec in manifest:
        ds_coords = tuple(manifest[ds_spec]["coords"])
        print(f"\n[*] Logic '{ds_spec}' anchored at {ds_coords}")
        ds_node = FSOFabricNode(ds_coords, m_val)

        # Load a tiny dataset
        ds_payload = {
            "call_spec": ds_spec,
            "data": {
                "path": "rotten_tomatoes",
                "split": "train[:1]"
            }
        }
        ds_packet = FSODataStream.create_packet(ds_payload, ds_coords, color=COLOR_LOGIC)

        print(f"[*] Dispatching Logic Wave to {ds_coords} for dataset loading...")
        ds_response = await ds_node.route_packet(ds_packet)

        if ds_response["status"] == "EXECUTED":
             print(f"[+] Success! Dataset loaded.")
             ds = ds_response["result"]
             print(f"    Sample: {ds[0]}")
        else:
             print(f"[!] Dataset loading failed: {ds_response}")

if __name__ == "__main__":
    asyncio.run(verify_hf_fso())
