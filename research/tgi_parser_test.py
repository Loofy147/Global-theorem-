import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tgi_parser import TGIParser
from tgi_core import TGICore

def test_parser_routing():
    print("═══ TGI-PARSER ROUTING TEST ═══")
    parser = TGIParser()

    # 1. Test Math routing
    parsed = parser.parse_input("x^2 + 2 = 11")
    print(f"Math input: domain={parsed['domain']}, m={parsed['m']}, k={parsed['k']}")
    assert parsed['domain'] == "math"
    assert parsed['m'] == 9

    # 2. Test Language routing
    parsed = parser.parse_input("This is topological intelligence.")
    print(f"Text input: domain={parsed['domain']}, m={parsed['m']}, k={parsed['k']}")
    assert parsed['domain'] == "language"
    assert parsed['m'] == 25

    # 3. Test Binary routing
    parsed = parser.parse_input("1010101")
    print(f"Binary input: domain={parsed['domain']}, m={parsed['m']}, k={parsed['k']}")
    assert parsed['domain'] == "binary"
    assert parsed['m'] == 2

    # 4. Test Lattice routing
    parsed = parser.parse_input({"points": []})
    print(f"Lattice input: domain={parsed['domain']}, m={parsed['m']}, k={parsed['k']}")
    assert parsed['domain'] == "lattice"
    assert parsed['m'] == 4

    print("═══ TGI-PARSER ROUTING SUCCESSFUL ═══")

if __name__ == "__main__":
    test_parser_routing()
