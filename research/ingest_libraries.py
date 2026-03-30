import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.knowledge_mapper import KnowledgeMapper

def ingest():
    km = KnowledgeMapper()

    libraries = [
        {
            "name": "NumPy",
            "id": "/numpy/numpy",
            "description": "Fundamental package for scientific computing with Python, providing N-dimensional arrays and linear algebra.",
            "snippets": 6139,
            "domain": "math"
        },
        {
            "name": "Kivy",
            "id": "/kivy/kivy",
            "description": "Open-source Python framework for cross-platform GUI applications (desktop, mobile, embedded).",
            "snippets": 1139,
            "domain": "ui"
        },
        {
            "name": "psutil",
            "id": "/giampaolo/psutil",
            "description": "Cross-platform library for retrieving information on running processes and system utilization (CPU, memory, sensors).",
            "snippets": 542,
            "domain": "hardware"
        },
        {
            "name": "SymPy",
            "id": "/sympy/sympy",
            "description": "Python library for symbolic mathematics, providing computer algebra system (CAS) capabilities.",
            "snippets": 1200, # Estimated
            "domain": "math"
        }
    ]

    for lib in libraries:
        km.ingest_library(lib)

    km.save_state()
    print(f"Ingested {len(libraries)} libraries into the LIBRARY fiber.")

if __name__ == "__main__":
    ingest()
