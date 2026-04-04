FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Pre-install core dependencies
RUN pip install --no-cache-dir numpy sympy pandas pillow matplotlib scipy scikit-learn pytest pytest-asyncio huggingface_hub anyio aiohttp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# HF Spaces usually use port 7860
ENV PORT=7860
EXPOSE 7860

CMD ["python3", "research/fso_global_node.py"]
