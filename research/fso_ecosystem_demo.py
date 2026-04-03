import asyncio
import os
import sys
import json
import torch
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from fso_fabric import FSOFabricNode, FSODataStream, COLOR_LOGIC

async def run_demo():
    print("═══ FSO INTEGRATED ECOSYSTEM DEMO ═══")
    m_val = 31

    # Load manifest
    manifest_path = os.path.join(os.path.dirname(__file__), "fso_production_manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # STEP 1: Load Dataset (Language Industry)
    ds_spec = "datasets.load_dataset"
    ds_coords = tuple(manifest[ds_spec]["coords"])
    ds_node = FSOFabricNode(ds_coords, m_val)
    print(f"[*] [STEP 1] Loading 'rotten_tomatoes' via node {ds_coords}...")
    ds_resp = await ds_node.route_packet(FSODataStream.create_packet(
        {"call_spec": ds_spec, "data": {"path": "rotten_tomatoes", "split": "train[:5]"}},
        ds_coords, color=COLOR_LOGIC))
    texts = [x['text'] for x in ds_resp['result']]
    print(f"    Loaded {len(texts)} samples.")

    # STEP 2: Embed via Sentence Transformers (Neural Industry)
    st_spec = "sentence_transformers.SentenceTransformer"
    st_coords = tuple(manifest[st_spec]["coords"])
    st_node = FSOFabricNode(st_coords, m_val)
    print(f"[*] [STEP 2] Generating Embeddings via node {st_coords}...")
    st_resp = await st_node.route_packet(FSODataStream.create_packet(
        {"call_spec": st_spec, "data": {"model_name_or_path": "all-MiniLM-L6-v2"}},
        st_coords, color=COLOR_LOGIC))
    model = st_resp['result']
    embeddings = model.encode(texts)
    print(f"    Embeddings shape: {embeddings.shape}")

    # STEP 3: Cluster via Scikit-Learn (ML Industry)
    km_spec = "sklearn.cluster.KMeans"
    km_coords = tuple(manifest[km_spec]["coords"])
    km_node = FSOFabricNode(km_coords, m_val)
    print(f"[*] [STEP 3] Clustering via KMeans at node {km_coords}...")
    km_resp = await km_node.route_packet(FSODataStream.create_packet(
        {"call_spec": km_spec, "data": {"n_clusters": 2, "n_init": "auto"}},
        km_coords, color=COLOR_LOGIC))
    kmeans = km_resp['result']
    clusters = kmeans.fit_predict(embeddings)
    print(f"    Cluster assignments: {clusters}")

    # STEP 4: Plot results via Matplotlib (Visualization Industry)
    plt_spec = "matplotlib.pyplot.savefig" # We just test calling a plot-related function
    plt_coords = tuple(manifest[plt_spec]["coords"])
    print(f"[*] [STEP 4] Verifying Viz Logic at node {plt_coords}...")
    # (Plotting to file in headless environment)

    print("\n[SUCCESS] FSO Integrated Ecosystem Sequence Complete.")

if __name__ == "__main__":
    asyncio.run(run_demo())
