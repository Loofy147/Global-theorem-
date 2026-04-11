import unittest
import json
import os
import sys
from unittest.mock import MagicMock

# Mock aiohttp and other missing dependencies
sys.modules['aiohttp'] = MagicMock()
sys.modules['aiohttp.web'] = MagicMock()
sys.modules['transformers'] = MagicMock()
sys.modules['torch'] = MagicMock()

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from research.fso_global_node import GlobalFSONode
from research.fso_apex_hypervisor import FSO_Apex_Hypervisor

class TestDecentralizedOps(unittest.TestCase):
    def setUp(self):
        self.m = 11
        # Mocking requirements for GlobalFSONode
        self.node = GlobalFSONode(self.m)
        self.hypervisor = FSO_Apex_Hypervisor(self.m)
        self.state_path = "fso_manifold_state_test.json"
        self.hypervisor.state_path = self.state_path

        # Mock state
        self.test_state = {
            "m_size": self.m,
            "registry": {
                "(0, 0, 0)": "project.test.logic"
            }
        }
        with open(self.state_path, "w") as f:
            json.dump(self.test_state, f)

    def tearDown(self):
        if os.path.exists(self.state_path):
            os.remove(self.state_path)

    def test_gossip_merge(self):
        """Verify that a node can merge peer directories correctly."""
        remote_dir = {"(1, 2, 3)": "192.168.1.100", "(4, 5, 6)": "192.168.1.101"}
        self.node._merge_peers(remote_dir)

        self.assertIn((1, 2, 3), self.node.peer_directory)
        self.assertEqual(self.node.peer_directory[(1, 2, 3)], "192.168.1.100")
        self.assertIn((4, 5, 6), self.node.peer_directory)

    def test_auditor_healing(self):
        """Verify that the auditor detects drift and corrects it."""
        logic_id = "project.test.logic"
        # Calculate real coords
        real_coords = self.hypervisor.topo.get_coords(logic_id)
        drifted_coords_str = "(9, 9, 9)" # Definitely wrong for m=11 and this ID

        # Inject drift into mock state
        self.test_state["registry"] = {drifted_coords_str: logic_id}
        with open(self.state_path, "w") as f:
            json.dump(self.test_state, f)

        # Run heal manually
        self.hypervisor._heal_drift(logic_id, real_coords, drifted_coords_str, self.test_state)

        # Reload and check
        with open(self.state_path, "r") as f:
            healed_state = json.load(f)

        self.assertNotIn(drifted_coords_str, healed_state["registry"])
        self.assertIn(str(real_coords), healed_state["registry"])
        self.assertEqual(healed_state["registry"][str(real_coords)], logic_id)
        self.assertEqual(healed_state["audit_healed"], 1)

if __name__ == "__main__":
    unittest.main()
