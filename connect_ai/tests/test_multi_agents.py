import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from connect_ai.agent.multi_agents import ManagerAgent


class MultiAgentTest(unittest.TestCase):
    def test_manager_dispatches(self):
        manager = ManagerAgent()
        result = manager.dispatch("recommend someone interesting")
        self.assertIn("tool", result)
        self.assertIn("data", result)


if __name__ == "__main__":
    unittest.main()
