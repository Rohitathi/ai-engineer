import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from production import build_readiness_payload


class ProductionComponentsTest(unittest.TestCase):
    def test_readiness_payload_reports_optional_services(self):
        payload = build_readiness_payload()
        self.assertIn("redis", payload)
        self.assertIn("kafka", payload)
        self.assertIn("mlops", payload)
        self.assertIn("github_sync", payload)


if __name__ == "__main__":
    unittest.main()
