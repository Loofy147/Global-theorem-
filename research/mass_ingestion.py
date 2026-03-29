import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tgi_agent import TGIAgent

def mass_populate():
    agent = TGIAgent()
    print("═══ TGI MASS KNOWLEDGE EXPANSION ═══")

    # 1. Physics & Universal Laws (LAW_MATH)
    physics = [
        ("Second_Law_Thermodynamics", "Entropy of an isolated system always increases."),
        ("General_Relativity", "Gravity is the curvature of spacetime manifold."),
        ("Quantum_Superposition", "Linear combination of state vectors in Hilbert space."),
        ("Maxwell_Equations", "Foundational laws of electromagnetism."),
        ("Schrodinger_Equation", "Evolution of the wave function in quantum mechanics."),
        ("Noether_Theorem", "Every differentiable symmetry has a corresponding conservation law."),
        ("Heisenberg_Uncertainty", "Limits on precision of conjugate variables."),
        ("Shannon_Entropy", "Measure of information content and uncertainty."),
        ("Yang_Mills_Theory", "Gauge theory for strong and weak nuclear forces.")
    ]
    for name, desc in physics:
        agent.ingest_knowledge("LAW_MATH", name, desc)

    # 2. Computer Science (TECHNOLOGY)
    cs = [
        ("P_vs_NP", "Foundational question of computational complexity."),
        ("Turing_Completeness", "System's ability to simulate any Turing machine."),
        ("CAP_Theorem", "Consistency, Availability, Partition tolerance trade-offs."),
        ("Byzantine_Fault_Tolerance", "Reliability in distributed systems with malicious actors."),
        ("Lambda_Calculus", "Formal system for function definition and application."),
        ("Von_Neumann_Architecture", "Instruction/data stored in shared memory."),
        ("RISC_V", "Open standard instruction set architecture."),
        ("Kernel_Space", "Privileged execution level for OS cores."),
        ("Graph_Neural_Networks", "Lifting neural weights to graph structures.")
    ]
    for name, desc in cs:
        agent.ingest_knowledge("TECHNOLOGY", name, desc)

    # 3. Systems Architecture (TECHNOLOGY)
    arch = [
        ("Microservices", "Decomposing apps into independent functional units."),
        ("Serverless_Computing", "Event-driven execution without infrastructure management."),
        ("Event_Sourcing", "State persistence as a sequence of events."),
        ("Kubernetes_Orchestration", "Automated scaling and management of containers."),
        ("Blockchain_Consensus", "Distributed agreement on state transitions."),
        ("Hardware_Abstraction_Layer", "Mediating between software and physical hardware."),
        ("Single_Instruction_Multiple_Data", "Parallel processing at the register level."),
        ("Zero_Knowledge_Proofs", "Proving knowledge without revealing the secret."),
        ("Virtual_Memory_Management", "Paging and segmentation of address spaces.")
    ]
    for name, desc in arch:
        agent.ingest_knowledge("TECHNOLOGY", name, desc)

    # 4. Biology & Life Sciences (LAW_MATH / DATASET)
    bio = [
        ("DNA_Replication", "Semi-conservative duplication of the genetic manifold."),
        ("Protein_Folding_Problem", "Predicting 3D structure from 1D amino acid sequence."),
        ("CRISPR_Cas9", "Programmable genomic editing technology."),
        ("Neural_Plasticity", "Ability of the brain manifold to reorganize structures."),
        ("Mendelian_Inheritance", "Laws of segregation and independent assortment."),
        ("Endosymbiosis_Theory", "Origin of eukaryotic organelles."),
        ("Metabolic_Pathways", "Topological graphs of biochemical reactions.")
    ]
    for name, desc in bio:
        agent.ingest_knowledge("LAW_MATH", name, desc)

    # 5. Advanced Relations
    relations = [
        ("General_Relativity", "Maxwell_Equations", "Unified Field Context"),
        ("Shannon_Entropy", "Second_Law_Thermodynamics", "Information-Energy Link"),
        ("Turing_Completeness", "Lambda_Calculus", "Equivalence"),
        ("Byzantine_Fault_Tolerance", "Blockchain_Consensus", "Implementation Base"),
        ("Neural_Plasticity", "Graph_Neural_Networks", "Biological Inspiration"),
        ("Virtual_Memory_Management", "Hardware_Abstraction_Layer", "Resource Control"),
        ("DNA_Replication", "CRISPR_Cas9", "Target Mechanism")
    ]
    for a, b, t in relations:
        agent.forge_relation(a, b, t)

    agent.core.ontology.save_state()
    print(f"\n[SUCCESS] Mass expansion complete. Current summary:")
    print(agent.ontology_summary())

if __name__ == "__main__":
    mass_populate()

def forge_cross_domain():
    agent = TGIAgent()
    cross_relations = [
        ("Quantum_Superposition", "Lambda_Calculus", "Computational Formalism"),
        ("Shannon_Entropy", "Graph_Neural_Networks", "Information Flow Metric"),
        ("Second_Law_Thermodynamics", "Basin_Escape_v3", "Stochastic Driving Force"),
        ("Metabolic_Pathways", "Event_Sourcing", "State Transition Mapping"),
        ("Endosymbiosis_Theory", "Microservices", "Evolutionary Modularization"),
        ("Mendelian_Inheritance", "Algebraic_Atlas", "Combinatorial Encoding"),
        ("General_Relativity", "Topological_Language_Model", "Manifold Curvature Analogy"),
        ("Noether_Theorem", "Blockchain_Consensus", "Invariance Guarantee"),
        ("P_vs_NP", "Spike_Construction", "Complexity Boundary Analysis"),
        ("Byzantine_Fault_Tolerance", "Hardware_Abstraction_Layer", "Robust System Interface")
    ]
    print("\n--- Forging Cross-Domain Topological Relations ---")
    for a, b, t in cross_relations:
        print(agent.forge_relation(a, b, t))
    agent.core.ontology.save_state()
    print(f"\n[FINAL] Ontology now contains {len(agent.core.ontology.grid)} entities.")

if __name__ == "__main__":
    # mass_populate()
    forge_cross_domain()
