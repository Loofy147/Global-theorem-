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

    # Login to HF to ensure full access
    from huggingface_hub import login
    login('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')

    # Load manifest to get coordinates
    manifest_path = os.path.join(os.path.dirname(__file__), "fso_production_manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # 1. Verify 'transformers.pipeline'
    hf_spec = "transformers.pipeline"
    if hf_spec in manifest:
        coords = tuple(manifest[hf_spec]["coords"])
        print(f"[*] Logic '{hf_spec}' anchored at {coords}")
        node = FSOFabricNode(coords, m_val)
        payload = {
            "call_spec": hf_spec,
            "data": {
                "task": "sentiment-analysis",
                "model": "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
            }
        }
        packet = FSODataStream.create_packet(payload, coords, color=COLOR_LOGIC)
        response = await node.route_packet(packet)
        if response["status"] == "EXECUTED":
            if isinstance(response["result"], str) and "ERROR" in response["result"]:
                 print(f"[!] Error in result: {response['result']}")
            else:
                 print(f"[+] Success! Sentiment Analysis Result: {response['result']('FSO is great!')}")

    # 2. Verify 'datasets.load_dataset'
    ds_spec = "datasets.load_dataset"
    if ds_spec in manifest:
        ds_coords = tuple(manifest[ds_spec]["coords"])
        print(f"\n[*] Logic '{ds_spec}' anchored at {ds_coords}")
        ds_node = FSOFabricNode(ds_coords, m_val)
        ds_payload = {"call_spec": ds_spec, "data": {"path": "rotten_tomatoes", "split": "train[:1]"}}
        ds_packet = FSODataStream.create_packet(ds_payload, ds_coords, color=COLOR_LOGIC)
        ds_response = await ds_node.route_packet(ds_packet)
        if ds_response["status"] == "EXECUTED":
             if isinstance(ds_response["result"], str) and "ERROR" in ds_response["result"]:
                  print(f"[!] Dataset error: {ds_response['result']}")
             else:
                  print(f"[+] Success! Dataset Sample: {ds_response['result'][0]}")

    # 3. Verify 'sentence_transformers.SentenceTransformer'
    st_spec = "sentence_transformers.SentenceTransformer"
    if st_spec in manifest:
        st_coords = tuple(manifest[st_spec]["coords"])
        print(f"\n[*] Logic '{st_spec}' anchored at {st_coords}")
        st_node = FSOFabricNode(st_coords, m_val)
        st_payload = {"call_spec": st_spec, "data": {"model_name_or_path": "all-MiniLM-L6-v2"}}
        st_packet = FSODataStream.create_packet(st_payload, st_coords, color=COLOR_LOGIC)
        st_response = await st_node.route_packet(st_packet)
        if st_response["status"] == "EXECUTED":
            if isinstance(st_response["result"], str) and "ERROR" in st_response["result"]:
                 print(f"[!] ST Error: {st_response['result']}")
            else:
                 print(f"[+] Success! Sentence Transformer loaded.")
                 model = st_response["result"]
                 embeddings = model.encode(["FSO Hamiltonian Cycle", "Topological General Intelligence"])
                 print(f"    Embeddings shape: {embeddings.shape}")

    # 4. Verify 'timm.create_model'
    timm_spec = "timm.create_model"
    if timm_spec in manifest:
        timm_coords = tuple(manifest[timm_spec]["coords"])
        print(f"\n[*] Logic '{timm_spec}' anchored at {timm_coords}")
        timm_node = FSOFabricNode(timm_coords, m_val)
        timm_payload = {"call_spec": timm_spec, "data": {"model_name": "resnet18", "pretrained": False}}
        timm_packet = FSODataStream.create_packet(timm_payload, timm_coords, color=COLOR_LOGIC)
        timm_response = await timm_node.route_packet(timm_packet)
        if timm_response["status"] == "EXECUTED":
             if isinstance(timm_response["result"], str) and "ERROR" in timm_response["result"]:
                  print(f"[!] TIMM Error: {timm_response['result']}")
             else:
                  print(f"[+] Success! TIMM Model loaded: {type(timm_response['result'])}")

    # 5. Verify 'huggingface_hub.whoami'
    hub_spec = "huggingface_hub.whoami"
    if hub_spec in manifest:
        hub_coords = tuple(manifest[hub_spec]["coords"])
        print(f"\n[*] Logic '{hub_spec}' anchored at {hub_coords}")
        hub_node = FSOFabricNode(hub_coords, m_val)
        hub_packet = FSODataStream.create_packet({"call_spec": hub_spec, "data": {}}, hub_coords, color=COLOR_LOGIC)
        hub_response = await hub_node.route_packet(hub_packet)
        if hub_response["status"] == "EXECUTED":
             print(f"[+] Hub Response (Identity): {hub_response['result'].get('name')}")

if __name__ == "__main__":
    asyncio.run(verify_hf_fso())
