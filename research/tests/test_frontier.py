import unittest
import numpy as np
import cmath
import sys, os

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from research.non_abelian_bridge import NonAbelianHilbertBridge
from research.tgi_parser import TGIParser
from research.tgi_core import TGICore

class TestFrontierCore(unittest.TestCase):
    def setUp(self):
        self.bridge = NonAbelianHilbertBridge(m=3, dimension=128)
        self.parser = TGIParser()
        self.core = TGICore()

    def test_heisenberg_holonomy(self):
        """Verify that Heisenberg loops produce non-trivial holonomy."""
        m = 3
        # Loop: [A, B] = C
        path = [(1,0,0), (0,1,0), (m-1,0,0), (0,m-1,0)]
        holonomy = self.bridge.calculate_holonomy(path)

        # In a non-abelian group, the geometric phase should be non-zero
        self.assertNotAlmostEqual(abs(holonomy), 1.0, places=5)
        # Note: Check if holonomy is at least slightly complex
        self.assertTrue(abs(holonomy) < 0.999)

    def test_spectral_projection(self):
        """Verify that intents are projected into normalized waveforms."""
        intent_vec = np.random.rand(128)
        waveform = self.bridge.project_to_functional_spectrum(intent_vec)

        self.assertEqual(len(waveform), 128)
        self.assertAlmostEqual(np.linalg.norm(waveform), 1.0, places=5)

    def test_parser_routing(self):
        """Verify that frontier keywords route correctly."""
        inputs = [
            "The infinite-dimensional Hilbert trajectory",
            "Non-abelian holonomy and resonance",
            "Langlands bridge synthesis"
        ]
        for inp in inputs:
            parsed = self.parser.parse_input(inp)
            self.assertEqual(parsed["domain"], "frontier")
            self.assertEqual(parsed["target_core"], "Frontier")

    def test_core_frontier_integration(self):
        """Verify that TGICore can process frontier intents."""
        intent = "Search for analytic omniscience frontier"
        self.core.reason_on(intent, solve_manifold=True)
        # Should not crash and should indicate Frontier Core
        self.assertEqual(self.core.parser.parse_input(intent)["target_core"], "Frontier")

if __name__ == "__main__":
    unittest.main()
