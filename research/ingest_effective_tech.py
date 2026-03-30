import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.knowledge_mapper import KnowledgeMapper

def ingest():
    km = KnowledgeMapper()

    # 1. TECHNOLOGY Fiber (FIBER 1)
    technologies = [
        {"name": "RAG", "payload": "Retrieval-Augmented Generation: Enhancing LLMs with external knowledge retrieval."},
        {"name": "LoRA", "payload": "Low-Rank Adaptation: Efficient fine-tuning of large models by updating low-rank matrices."},
        {"name": "QLoRA", "payload": "Quantized LoRA: Efficient fine-tuning with 4-bit quantization."},
        {"name": "Mamba", "payload": "Selective State Space Models: Linear-time alternative to Transformers for long sequences."},
        {"name": "Flash_Attention", "payload": "Memory-efficient and fast implementation of the attention mechanism."},
        {"name": "Transformer", "payload": "The foundational architecture for modern LLMs using self-attention."},
        {"name": "SES", "payload": "Short Exact Sequence: A sequence of objects and morphisms where the image of one equals the kernel of the next (0 -> H -> G -> Q -> 0)."},
        {"name": "Cohomology", "payload": "A tool in algebraic topology for measuring global structural obstructions (e.g., H^2 for central extensions)."},
        {"name": "Hamiltonian_Cycle", "payload": "A path in a graph that visits every vertex exactly once, foundational to TGI navigation."},
        {"name": "RLHF", "payload": "Reinforcement Learning from Human Feedback: Aligning LLMs with human preferences."},
        {"name": "PPO", "payload": "Proximal Policy Optimization: A stable reinforcement learning algorithm used in LLM alignment."},
        {"name": "Diffusion_Models", "payload": "Generative models that create data by reversing a noise-adding process."},
        {"name": "Quantization", "payload": "Reducing the precision of model weights (e.g., FP16 to INT8) to save memory and compute."},
        {"name": "Topological_General_Intelligence", "payload": "Reasoning via algebraic lifting and manifold navigation (TGI)."}
    ]
    for tech in technologies:
        km.ingest_concept("TECHNOLOGY", tech["name"], tech["payload"])

    # 2. LIBRARY Fiber (FIBER 7)
    libraries = [
        {"name": "Pandas", "domain": "data", "description": "Powerful data manipulation and analysis library for Python."},
        {"name": "Polars", "domain": "data", "description": "Lightning-fast DataFrame library written in Rust."},
        {"name": "PyTorch", "domain": "ai", "description": "Flexible deep learning framework with dynamic computational graphs."},
        {"name": "TensorFlow", "domain": "ai", "description": "Comprehensive open-source platform for machine learning."},
        {"name": "Transformers", "domain": "ai", "description": "State-of-the-art machine learning for Pytorch, TensorFlow, and JAX."},
        {"name": "FastAPI", "domain": "web", "description": "Modern, fast (high-performance) web framework for building APIs with Python 3.8+."},
        {"name": "Django", "domain": "web", "description": "High-level Python web framework that encourages rapid development and clean design."},
        {"name": "Scikit-Learn", "domain": "math", "description": "Simple and efficient tools for predictive data analysis."},
        {"name": "Matplotlib", "domain": "viz", "description": "Comprehensive library for creating static, animated, and interactive visualizations in Python."},
        {"name": "Seaborn", "domain": "viz", "description": "Statistical data visualization library based on matplotlib."},
        {"name": "Plotly", "domain": "viz", "description": "Interactive, open-source plotting library for Python."},
        {"name": "BeautifulSoup", "domain": "web", "description": "Library for pulling data out of HTML and XML files."},
        {"name": "Requests", "domain": "web", "description": "Simple, yet elegant, HTTP library for Python."},
        {"name": "SQLAlchemy", "domain": "db", "description": "The Python SQL Toolkit and Object Relational Mapper."},
        {"name": "Pydantic", "domain": "data", "description": "Data validation and settings management using Python type annotations."},
        {"name": "Celery", "domain": "infra", "description": "Distributed task queue for Python."},
        {"name": "Redis-py", "domain": "infra", "description": "Python client for Redis key-value store."}
    ]
    for lib in libraries:
        km.ingest_library(lib)

    # 3. API_MCP Fiber (FIBER 6)
    # Render MCP Tools
    render_tools = [
        "render_create_web_service", "render_get_service", "render_list_services", "render_update_web_service",
        "render_create_static_site", "render_update_static_site", "render_create_postgres", "render_get_postgres",
        "render_list_postgres_instances", "render_query_render_postgres", "render_create_key_value", "render_get_key_value",
        "render_list_key_value", "render_create_cron_job", "render_update_cron_job", "render_list_workspaces",
        "render_get_selected_workspace", "render_select_workspace", "render_list_deploys", "render_get_deploy",
        "render_list_logs", "render_list_log_label_values", "render_update_environment_variables", "render_get_metrics"
    ]
    for tool in render_tools:
        km.ingest_concept("API_MCP", tool, {"name": tool, "domain": "cloud"})

    # Supabase MCP Tools
    supabase_tools = [
        "supabase_list_organizations", "supabase_get_organization", "supabase_list_projects", "supabase_get_project",
        "supabase_get_cost", "supabase_confirm_cost", "supabase_create_project", "supabase_pause_project",
        "supabase_restore_project", "supabase_list_tables", "supabase_list_extensions", "supabase_list_migrations",
        "supabase_apply_migration", "supabase_execute_sql", "supabase_get_logs", "supabase_get_advisors",
        "supabase_get_project_url", "supabase_get_publishable_keys", "supabase_generate_typescript_types",
        "supabase_list_edge_functions", "supabase_get_edge_function", "supabase_deploy_edge_function",
        "supabase_create_branch", "supabase_list_branches", "supabase_delete_branch", "supabase_merge_branch",
        "supabase_reset_branch", "supabase_rebase_branch", "supabase_search_docs"
    ]
    for tool in supabase_tools:
        km.ingest_concept("API_MCP", tool, {"name": tool, "domain": "db"})

    # Context7 Tools
    context7_tools = ["context7_resolve_library_id", "context7_query_docs"]
    for tool in context7_tools:
        km.ingest_concept("API_MCP", tool, {"name": tool, "domain": "docs"})

    km.save_state()
    print(f"Ingested {len(technologies)} technologies, {len(libraries)} libraries, and {len(render_tools) + len(supabase_tools) + len(context7_tools)} MCP tools.")

if __name__ == "__main__":
    ingest()

def ingest_extra():
    km = KnowledgeMapper()
    extra_tech = [
        {"name": "Project_ELECTRICITY", "payload": "A logic framework for mapping all datasets, laws, and designs into TGI functional fibers."},
        {"name": "Mobile_Genesis", "payload": "Phase 6 of TGI development: Hardware-aware manifolds and mobile-first agentic actions."},
        {"name": "Full_Autonomy", "payload": "Phase 7 of TGI development: Autonomous task completion via topological path lifting."},
        {"name": "Action_Coordinate_Mapping", "payload": "The deterministic translation of Hamiltonian paths into system-level agentic actions."},
        {"name": "Topological_Attention", "payload": "A mechanism for weighting semantic fibers by gauge multiplicity (W4) during linguistic generation."}
    ]
    for tech in extra_tech:
        km.ingest_concept("TECHNOLOGY", tech["name"], tech["payload"])
    km.save_state()
    print(f"Ingested {len(extra_tech)} extra technologies.")

if __name__ == "__main__":
    ingest()
    ingest_extra()
