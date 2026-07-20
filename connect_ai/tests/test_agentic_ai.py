import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from connect_ai.agent.agent import ConnectAgent


class AgenticAITest(unittest.TestCase):
    def test_agent_handles_simple_input(self):
        agent = ConnectAgent()
        result = agent.run("hello")
        self.assertIn("reply", result)
        self.assertIsInstance(result["reply"], str)


if __name__ == "__main__":
    unittest.main()
