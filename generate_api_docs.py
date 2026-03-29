import ast
import os

def get_docstring(node):
    return ast.get_docstring(node) or "No description."

def format_args(args):
    arg_names = [a.arg for a in args.args]
    if args.vararg:
        arg_names.append("*" + args.vararg.arg)
    if args.kwarg:
        arg_names.append("**" + args.kwarg.arg)
    return ", ".join(arg_names)

def parse_file(filename):
    with open(filename, "r") as f:
        tree = ast.parse(f.read())

    docs = []
    docs.append(f"## {filename}")
    file_doc = get_docstring(tree)
    if file_doc:
        docs.append(file_doc)
        docs.append("")

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            sig = f"### `def {node.name}({format_args(node.args)})`"
            docs.append(sig)
            docs.append(get_docstring(node))
            docs.append("")
        elif isinstance(node, ast.ClassDef):
            docs.append(f"### `class {node.name}`")
            docs.append(get_docstring(node))
            docs.append("")
            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    sig = f"#### `def {node.name}.{subnode.name}({format_args(subnode.args)})`"
                    docs.append(sig)
                    docs.append(get_docstring(subnode))
                    docs.append("")
    return "\n".join(docs)

# Add TGI modules
files = ['core.py', 'engine.py', 'frontiers.py', 'search.py', 'theorems.py', 'domains.py', 'fiber.py',
         'research/tgi_core.py', 'research/tlm.py', 'research/tgi_parser.py', 'research/tgi_agent.py']
full_docs = ["# API Documentation\n"]
for f in files:
    if os.path.exists(f):
        full_docs.append(parse_file(f))

with open("docs/API.md", "w") as f:
    f.write("\n".join(full_docs))
