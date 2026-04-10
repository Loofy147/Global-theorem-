import ast
import hashlib
import os
from typing import Dict, Any, List, Tuple
from multiprocessing import Pool, cpu_count

class FSORefinery:
    """
    The tool used by the Agent to 'smelt' GitHub repos into FSO Logic.
    It breaks libraries into atomic functions/classes and assigns Hamiltonian Coords.
    """
    def __init__(self, m: int):
        self.m = m

    def refinery_process(self, source_dir: str) -> List[Dict[str, Any]]:
        """
        Walks through a production repo, extracts logic units, and
        prepares them for Hamiltonian Injection. Parallelized with multiprocessing.
        """
        all_py_files = []
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".py"):
                    all_py_files.append(os.path.join(root, file))

        # Parallelize file smelting
        with Pool(processes=cpu_count()) as pool:
            # results is a list of lists of dicts
            results = pool.map(self._smelt_file, all_py_files)

        # Flatten the list
        logic_units = [unit for sublist in results for unit in sublist]
        return logic_units

    def _smelt_file(self, filepath: str) -> List[Dict[str, Any]]:
        units = []
        try:
            with open(filepath, "r") as f:
                content = f.read()
                tree = ast.parse(content)

                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        units.append(self._create_unit(node, filepath))
                    elif isinstance(node, ast.ClassDef):
                        # Add the class itself
                        units.append(self._create_unit(node, filepath))
                        # Add its methods
                        for subnode in node.body:
                            if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                units.append(self._create_unit(subnode, filepath, parent_class=node.name))
        except Exception:
            pass
        return units

    def _create_unit(self, node: Any, filepath: str, parent_class: str = None) -> Dict[str, Any]:
        name = node.name
        full_id = f"{parent_class}.{name}" if parent_class else name
        code = ast.unparse(node)

        # Docstring Synthesis (Color 1 - Generative)
        docstring = ast.get_docstring(node)
        if not docstring:
            docstring = self._synthesize_docstring(name, code)

        coords = self._calculate_coords(full_id)
        return {
            "id": full_id,
            "name": name,
            "parent": parent_class,
            "coords": coords,
            "fiber": sum(coords) % self.m,
            "logic": code,
            "docstring": docstring,
            "origin": filepath,
            "type": type(node).__name__
        }

    def _synthesize_docstring(self, name: str, code: str) -> str:
        """Simple rule-based docstring synthesis for unanchored logic."""
        if name.startswith("test_"):
            return f"Unit test for {name.replace('test_', '')}."
        if name.startswith("__"):
            return f"Internal or magic method: {name}."
        return f"Logic unit '{name}' extracted from source. Implementation details in code."

    def _calculate_coords(self, identifier: str) -> Tuple[int, int, int]:
        h = int(hashlib.sha256(identifier.encode()).hexdigest(), 16)
        return (h % self.m, (h // self.m) % self.m, (h // (self.m**2)) % self.m)

if __name__ == "__main__":
    m_val = 101 # Production-grade manifold size
    refinery = FSORefinery(m_val)
    print(f"Refinery initialized for m={m_val} ({m_val**3} total slots)")

    # Quick test on itself
    test_units = refinery._smelt_file(__file__)
    for unit in test_units:
        print(f"Extracted: {unit['id']} ({unit['type']}) - Coords: {unit['coords']}")
