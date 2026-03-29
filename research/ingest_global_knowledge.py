import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tgi_agent import TGIAgent
import json

def populate():
    agent = TGIAgent()

    print("═══ TGI GLOBAL KNOWLEDGE INGESTION ═══")

    # 1. LAW_MATH: Absolute Truths
    laws = [
        ("Closure_Lemma", "The k-1 dimension mathematically forces the k-th cycle closure."),
        ("Parity_Obstruction", "Manifolds G_m^k with even m and odd k are Hamiltonian-impossible."),
        ("Sylow_Theorems", "Governing conditions for the existence and number of subgroups."),
        ("H2_Cohomology", "The group of 2-cocycles that classifies central extensions."),
        ("Spike_Construction", "Deterministic O(m) method for 3-Hamiltonian decompositions."),
        ("Gauge_Multiplicity_W4", "The number of equivalent representations of a topological state."),
        ("Torsor_Structure_H1", "The moduli space of valid Hamiltonian decompositions.")
    ]
    for name, desc in laws:
        agent.ingest_knowledge("LAW_MATH", name, desc)

    # 2. TECHNOLOGY: Implementations
    tech = [
        ("Basin_Escape_v3", "Randomized orbit-flip engine for breaking local topological minima."),
        ("FSO_Compiler", "Converts high-level logical structures into coordinate-based manifolds."),
        ("Topological_Language_Model", "A linguistic engine where meaning is a fibration over a base group."),
        ("AIMO_Reasoning_Engine", "Hybrid symbolic-search solver for mathematical olympiads."),
        ("Knowledge_Mapper", "Topological ontology implementation for Project ELECTRICITY."),
        ("Tensor_Fibration", "Mapping of continuous neural weights into discrete group structures.")
    ]
    for name, desc in tech:
        agent.ingest_knowledge("TECHNOLOGY", name, desc)

    # 3. DATASET: Information
    datasets = [
        ("AIMO_Progress_Prize_3", "Collection of high-level competitive mathematical problems."),
        ("TSPLIB_Benchmarks", "Standardized instances for the Traveling Salesman Problem."),
        ("Sovereign_OS_Logs", "Topological route paths and system state histories."),
        ("Algebraic_Atlas", "Mapping of all solvable (m, k) parameters for abelian groups.")
    ]
    for name, desc in datasets:
        agent.ingest_knowledge("DATASET", name, desc)

    # 4. AESTHETICS: Design
    colors = [
        ("Sovereign_Gold", (212, 175, 55, 255)),
        ("Topological_Blue", (0, 102, 204, 255)),
        ("Obstruction_Red", (255, 0, 0, 255)),
        ("Solvable_Green", (50, 205, 50, 255))
    ]
    for name, rgba in colors:
        agent.query({"name": name, "rgba": rgba, "color": True})

    # 5. FORGING RELATIONS
    relations = [
        ("Closure_Lemma", "FSO_Compiler", "Theoretical Foundation"),
        ("Parity_Obstruction", "Basin_Escape_v3", "Optimization Target"),
        ("Spike_Construction", "AIMO_Reasoning_Engine", "Algorithmic Core"),
        ("Topological_Language_Model", "Tensor_Fibration", "Conceptual Bridge"),
        ("Knowledge_Mapper", "Sovereign_OS_Logs", "Index Engine")
    ]
    for a, b, t in relations:
        print(agent.forge_relation(a, b, t))

    agent.core.ontology.save_state()
    print(f"\n[SUCCESS] Ingested {len(agent.core.ontology.grid)} entities into the manifold.")

if __name__ == "__main__":
    populate()

def forge_more_relations():
    agent = TGIAgent()
    more_relations = [
        ("Sylow_Theorems", "Algebraic_Atlas", "Categorification"),
        ("H2_Cohomology", "Parity_Obstruction", "Structural Cause"),
        ("Gauge_Multiplicity_W4", "Basin_Escape_v3", "Search Space Metric"),
        ("Torsor_Structure_H1", "Spike_Construction", "Geometric Context"),
        ("AIMO_Progress_Prize_3", "AIMO_Reasoning_Engine", "Primary Benchmark")
    ]
    print("\n--- Forging Additional Relations ---")
    for a, b, t in more_relations:
        print(agent.forge_relation(a, b, t))
    agent.core.ontology.save_state()
    print(f"\n[UPDATED] Ontology now contains {len(agent.core.ontology.grid)} entities.")

if __name__ == "__main__":
    # populate()  # Already done
    forge_more_relations()
