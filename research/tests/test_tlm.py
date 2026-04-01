import pytest
import hashlib
from research.tlm import TopologicalLanguageModel

@pytest.fixture
def tlm():
    return TopologicalLanguageModel(m=11, k=3)

def test_tlm_initialization(tlm):
    assert tlm.m == 11
    assert tlm.k == 3
    assert tlm.ontology is not None

def test_tokenize(tlm):
    text = "TGI Agent"
    tokens = tlm.tokenize(text)
    assert len(tokens) == 2
    assert all(0 <= t < tlm.m for t in tokens)

def test_generate_path(tlm):
    path = tlm.generate_path("TGI", length=5)
    assert len(path) > 0
    assert len(path[0]) == 3

def test_generate(tlm):
    completion = tlm.generate("TGI", length=10)
    assert "TGI" in completion
    assert len(completion) > 3

def test_generate_ontology_grounded(tlm):
    tlm.ontology.grid = {} # Ensure clear state
    tlm.ontology.ingest_concept("LANGUAGE", "Topological", "Concept")
    tlm.ontology.ingest_concept("LANGUAGE", "General", "Concept")
    tlm.ontology.ingest_concept("LANGUAGE", "Intelligence", "Concept")

    completion = tlm.generate_ontology_grounded("TGI is", length=15)
    assert "TGI is" in completion

    words = ["Topological", "General", "Intelligence"]
    # Log the completion for debugging
    print(f"DEBUG completion: {completion}")
    assert any(w in completion for w in words)

def test_parity_obstruction():
    tlm_obs = TopologicalLanguageModel(m=10, k=3)
    path = tlm_obs.generate_path("test", length=5)
    assert path == []

    completion = tlm_obs.generate("test", length=5)
    assert "[TOPOLOGICAL_ERROR: H2_PARITY_OBSTRUCTED]" in completion
