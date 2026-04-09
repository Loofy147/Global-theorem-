import sys, os
import pandas as pd
import numpy as np
from datasets import load_dataset
from huggingface_hub import HfApi
import kaggle
from typing import Dict, List, Any

# Ensure we can import from the root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.tgi_agent import TGIAgent

def authenticate():
    # Credentials provided by user
    os.environ['KAGGLE_USERNAME'] = 'hichambedrani'
    os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_API_TOKEN')
    os.environ['HF_TOKEN'] = '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'
    print("[AUTH] Environment configured for Kaggle and Hugging Face.")

def ingest_hf_text(agent: TGIAgent, dataset_name: str = "fancyzhx/ag_news", num_samples: int = 20):
    print(f"\n--- Ingesting Text from HF: {dataset_name} ---")
    try:
        ds = load_dataset(dataset_name, split='train', streaming=True)
        samples = list(ds.take(num_samples))
        categories = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}

        for i, item in enumerate(samples):
            cat_name = categories.get(item['label'], "General")
            title = item['title']
            desc = item['description']

            # Map to DATASET fiber
            agent.ingest_knowledge("DATASET", f"AG_NEWS_{i}_{cat_name}", f"{title}: {desc}")
            if i % 5 == 0: print(f"  Ingested {i}/{num_samples} text samples...")

    except Exception as e:
        print(f"[ERROR] HF Text Ingestion failed: {e}")

def ingest_kaggle_csv(agent: TGIAgent, dataset_ref: str = "unsdsn/world-happiness", num_samples: int = 20):
    print(f"\n--- Ingesting Data from Kaggle: {dataset_ref} ---")
    try:
        # Download the 2019 data specifically
        kaggle.api.dataset_download_file(dataset_ref, '2019.csv', path='kaggle_data')
        df = pd.read_csv('kaggle_data/2019.csv').head(num_samples)

        for idx, row in df.iterrows():
            country = row['Country or region']
            score = row['Score']
            gdp = row['GDP per capita']

            # Map to DATASET fiber
            agent.ingest_knowledge("DATASET", f"Happiness_{country}", f"Score: {score}, GDP: {gdp}")
            if idx % 5 == 0: print(f"  Ingested {idx}/{num_samples} country samples...")

    except Exception as e:
        print(f"[ERROR] Kaggle Ingestion failed: {e}")

def ingest_hf_vision(agent: TGIAgent, dataset_name: str = "zalando-datasets/fashion_mnist", num_samples: int = 5):
    print(f"\n--- Ingesting Vision from HF: {dataset_name} ---")
    try:
        ds = load_dataset(dataset_name, split='train', streaming=True)
        samples = list(ds.take(num_samples))
        labels = {0: "T-shirt/top", 1: "Trouser", 2: "Pullover", 3: "Dress", 4: "Coat",
                  5: "Sandal", 6: "Shirt", 7: "Sneaker", 8: "Bag", 9: "Ankle boot"}

        for i, item in enumerate(samples):
            img = np.array(item['image'])
            label = labels.get(item['label'], "Unknown")

            # Use Vision Core to lift image
            res = agent.query(img)
            print(f"  Lifted {label} image to manifold: {res[:80]}...")

            # Also register in ontology
            agent.ingest_knowledge("AESTHETICS", f"Fashion_{i}_{label}", f"Topological Signature: {res}")

    except Exception as e:
        print(f"[ERROR] HF Vision Ingestion failed: {e}")

def main():
    authenticate()
    agent = TGIAgent()

    # 1. Hugging Face Text (AG News)
    ingest_hf_text(agent)

    # 2. Kaggle CSV (World Happiness)
    ingest_kaggle_csv(agent)

    # 3. Hugging Face Vision (Fashion MNIST)
    ingest_hf_vision(agent)

    # Save the expanded state
    agent.core.ontology.save_state()
    print("\n" + agent.ontology_summary())
    print(f"\n[FINAL] Massive Ingestion Complete. Total Entities: {len(agent.core.ontology.grid)}")

if __name__ == "__main__":
    main()
