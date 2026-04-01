import os
import json
import pytest
from research.knowledge_mapper import KnowledgeMapper

TEST_STATE_PATH = "research/tests/test_ontology.json"

@pytest.fixture
def km():
    if os.path.exists(TEST_STATE_PATH):
        os.remove(TEST_STATE_PATH)
    mapper = KnowledgeMapper(m=256, k=4, state_path=TEST_STATE_PATH)
    yield mapper
    if os.path.exists(TEST_STATE_PATH):
        os.remove(TEST_STATE_PATH)

def test_initialization(km):
    assert km.m == 256
    assert km.k == 4
    assert "LAW_MATH" in km.FIBERS
    assert km.grid == {}

def test_closure_hashing(km):
    target_fiber = km.FIBERS["TECHNOLOGY"]
    coord = km._apply_closure_hashing("TGI_Engine", target_fiber)
    assert len(coord) == 4
    assert sum(coord) % km.m == target_fiber

def test_ingest_concept(km):
    coord = km.ingest_concept("LAW_MATH", "Gravity", "9.8 m/s^2")
    assert str(coord) in km.grid
    assert km.grid[str(coord)]["name"] == "Gravity"
    assert km.grid[str(coord)]["fiber"] == km.FIBERS["LAW_MATH"]
    assert sum(coord) % km.m == km.FIBERS["LAW_MATH"]

def test_ingest_color(km):
    r, g, b, a = 100, 150, 200, 255
    coord = km.ingest_color("TGI_Blue", r, g, b, a)
    assert coord == (100, 150, 200, 255)
    assert str(coord) in km.grid
    assert km.grid[str(coord)]["name"] == "TGI_Blue"
    assert km.grid[str(coord)]["fiber"] == sum(coord) % km.m

def test_map_relation(km):
    km.ingest_concept("TECHNOLOGY", "TGI_Core", "Core Engine")
    km.ingest_concept("TECHNOLOGY", "TLM", "Language Model")
    vector = km.map_relation("TGI_Core", "TLM", "INTEGRATES")

    assert vector is not None
    assert len(vector) == 4
    # Check if the relation concept itself was ingested
    rel_name = "TGI_Core_to_TLM_INTEGRATES"
    assert km._find_coord(rel_name) is not None

def test_save_load_state(km):
    km.ingest_concept("DATASET", "Sample", "Data")
    km.save_state()
    assert os.path.exists(TEST_STATE_PATH)

    new_km = KnowledgeMapper(m=256, k=4, state_path=TEST_STATE_PATH)
    assert str(km._find_coord("Sample")) in new_km.grid
    assert new_km.grid[str(new_km._find_coord("Sample"))]["name"] == "Sample"
