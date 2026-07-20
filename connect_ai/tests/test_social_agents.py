import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from connect_ai.agent.multi_agents import ManagerAgent


class SocialAgentsTest(unittest.TestCase):
    def test_social_routes(self):
        manager = ManagerAgent()
        message_result = manager.dispatch("send a message")
        location_result = manager.dispatch("update location")
        nearby_result = manager.dispatch("find nearby users")
        search_result = manager.dispatch("search posts")

        self.assertEqual(message_result["tool"], "message")
        self.assertEqual(location_result["tool"], "location")
        self.assertEqual(nearby_result["tool"], "nearby_users")
        self.assertEqual(search_result["tool"], "search_nearby")


if __name__ == "__main__":
    unittest.main()
