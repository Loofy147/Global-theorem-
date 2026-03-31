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
    try:
        with open(filename, "r") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        return f"## {filename}\nError parsing file: {e}\n"

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

# Discover files
discovery_dirs = ['.', 'research']
all_files = []
for d in discovery_dirs:
    if os.path.isdir(d):
        files_in_dir = sorted(os.listdir(d))
        for f in files_in_dir:
            if f.endswith('.py') and not f.startswith('__'):
                path = os.path.join(d, f) if d != '.' else f
                if os.path.isfile(path):
                    all_files.append(path)

full_docs = ["# API Documentation\n"]
for f in all_files:
    full_docs.append(parse_file(f))

with open("docs/API.md", "w") as f:
    f.write("\n".join(full_docs))
print(f"Generated documentation for {len(all_files)} files.")
