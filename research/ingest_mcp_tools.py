import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.knowledge_mapper import KnowledgeMapper

def ingest():
    km = KnowledgeMapper()

    # 1. Render MCP Tools (Metadata)
    render_tools = [
        {"name": "render_create_web_service", "params": ["name", "runtime", "buildCommand"], "domain": "cloud"},
        {"name": "render_list_services", "params": [], "domain": "cloud"},
        {"name": "render_get_metrics", "params": ["resourceId"], "domain": "cloud"}
    ]
    km.ingest_mcp_tools(render_tools)

    # 2. Supabase MCP Tools (Metadata)
    supabase_tools = [
        {"name": "supabase_create_project", "params": ["name", "region"], "domain": "db"},
        {"name": "supabase_execute_sql", "params": ["project_id", "query"], "domain": "db"},
        {"name": "supabase_deploy_edge_function", "params": ["project_id", "name"], "domain": "db"}
    ]
    km.ingest_mcp_tools(supabase_tools)

    # 3. Context7 MCP Tools (Metadata)
    context7_tools = [
        {"name": "context7_resolve_library_id", "params": ["libraryName"], "domain": "docs"},
        {"name": "context7_query_docs", "params": ["libraryId", "query"], "domain": "docs"}
    ]
    km.ingest_mcp_tools(context7_tools)

    km.save_state()
    print(f"Ingested {len(render_tools) + len(supabase_tools) + len(context7_tools)} MCP tool signatures into API_MCP fiber.")

if __name__ == "__main__":
    ingest()
