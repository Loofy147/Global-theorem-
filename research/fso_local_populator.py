import json
import os
import sys
import hashlib
from typing import List, Dict

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from fso_direct_consumer import FSODirectConsumer

class FSOLocalPopulator:
    """
    Pre-loads hundreds of industrial library functions into a persistent manifest.
    Maps high-impact logic (NumPy, PyTorch, etc.) to the FSO Torus.
    """
    def __init__(self, m: int):
        self.m = m
        self.dc = FSODirectConsumer(m)
        self.manifest = {}

    def populate_library(self, lib_name: str, functions: List[str]):
        print(f"[*] Populating {lib_name}...")
        for func in functions:
            call_spec = f"{lib_name}.{func}" if func else lib_name
            coords = self.dc.get_coords(call_spec)
            self.manifest[call_spec] = {
                "coords": coords,
                "fiber": sum(coords) % self.m,
                "type": "direct_consumption"
            }

    def save_manifest(self, filepath: str):
        with open(filepath, "w") as f:
            json.dump(self.manifest, f, indent=4)
        print(f"[!] Saved {len(self.manifest)} industrial units to {filepath}")

if __name__ == "__main__":
    m_val = 31
    populator = FSOLocalPopulator(m_val)

    # 1. NumPy (Math Industry)
    populator.populate_library("numpy", [
        "fft.fft", "fft.ifft", "linalg.inv", "linalg.solve", "linalg.eig",
        "random.rand", "random.randn", "random.randint", "array", "mean", "std",
        "sum", "dot", "matmul", "reshape", "transpose", "concatenate", "stack"
    ])

    # 2. pandas (Data Industry)
    populator.populate_library("pandas", [
        "read_csv", "read_json", "read_parquet", "DataFrame", "Series",
        "concat", "merge", "pivot_table", "groupby", "to_csv", "to_json"
    ])

    # 3. PyTorch (Neural Industry)
    populator.populate_library("torch", [
        "nn.Linear", "nn.Conv2d", "nn.ReLU", "nn.CrossEntropyLoss", "nn.Module",
        "optim.Adam", "optim.SGD", "save", "load", "tensor", "cat", "stack",
        "cuda.is_available", "device", "from_numpy", "manual_seed"
    ])

    # 4. FastAPI (Web Industry)
    populator.populate_library("fastapi", [
        "FastAPI", "APIRouter", "Depends", "HTTPException", "Header",
        "Query", "Path", "Body", "Form", "File", "UploadFile"
    ])

    # 5. OpenCV (Vision Industry)
    populator.populate_library("cv2", [
        "imread", "imwrite", "imshow", "cvtColor", "GaussianBlur", "Canny",
        "findContours", "drawContours", "rectangle", "circle", "putText",
        "resize", "threshold", "bitwise_and", "bitwise_or", "absdiff"
    ])

    # 6. JSON & REST (System Industry)
    populator.populate_library("json", ["loads", "dumps", "load", "dump"])
    populator.populate_library("requests", ["get", "post", "put", "delete", "patch", "head"])

    # 7. Kotlin / Android (Mobile Industry - Symbolic)
    populator.populate_library("kotlin", [
        "stdlib.collections.map", "stdlib.collections.filter", "stdlib.text.replace",
        "coroutines.launch", "coroutines.async", "coroutines.runBlocking",
        "android.view.View", "android.widget.Button", "android.content.Intent"
    ])

    # 8. Hugging Face Transformers (Language & Multi-modal Industry)
    populator.populate_library("transformers", [
        "pipeline", "AutoModel", "AutoTokenizer", "AutoConfig",
        "Trainer", "TrainingArguments", "LlamaForCausalLM", "BertModel"
    ])

    # 9. Hugging Face Datasets (Data Industry)
    populator.populate_library("datasets", [
        "load_dataset", "load_from_disk", "list_datasets", "Dataset", "IterableDataset"
    ])

    # 10. Hugging Face Hub (Model Management)
    populator.populate_library("huggingface_hub", [
        "hf_hub_download", "snapshot_download", "login", "whoami", "list_models"
    ])

    # 11. Tokenizers (Tokenization Industry)
    populator.populate_library("tokenizers", [
        "Tokenizer", "models.BPE", "trainers.BpeTrainer", "pre_tokenizers.Whitespace"
    ])

    # 12. Diffusers (Generative Vision Industry)
    populator.populate_library("diffusers", [
        "StableDiffusionPipeline", "DiffusionPipeline", "AutoencoderKL", "UNet2DConditionModel"
    ])

    # 13. TIMM (Vision Models)
    populator.populate_library("timm", [
        "create_model", "list_models", "list_pretrained"
    ])

    # 14. Sentence Transformers (Embeddings Industry)
    populator.populate_library("sentence_transformers", [
        "SentenceTransformer", "util.cos_sim", "util.semantic_search"
    ])

    # 15. PEFT (Parameter-Efficient Fine-Tuning)
    populator.populate_library("peft", [
        "get_peft_model", "LoraConfig", "TaskType"
    ])

    # 16. Accelerate (Distributed Training)
    populator.populate_library("accelerate", [
        "Accelerator", "init_empty_weights", "load_checkpoint_and_dispatch"
    ])

    # 17. Evaluate (Model Evaluation Industry)
    populator.populate_library("evaluate", [
        "load", "list_evaluation_modules", "combine"
    ])

    # 18. Optimum (Hardware Optimization)
    populator.populate_library("optimum", [
        "pipelines.pipeline", "onnxruntime.ORTModelForCausalLM", "bettertransformer.BetterTransformer"
    ])

    # 19. TRL (Transformer Reinforcement Learning)
    populator.populate_library("trl", [
        "SFTTrainer", "RewardTrainer", "PPOTrainer", "AutoModelForCausalLMWithValueHead"
    ])

    # 20. bitsandbytes (Quantization Industry)
    populator.populate_library("bitsandbytes", [
        "nn.Linear8bitLt", "nn.Linear4bit", "optim.Adam8bit"
    ])

    # Save the manifest to research/fso_production_manifest.json
    manifest_path = os.path.join(os.path.dirname(__file__), "fso_production_manifest.json")
    populator.save_manifest(manifest_path)
