import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class ProductionEndpointsTest(unittest.TestCase):
    def test_metrics_endpoint_is_available(self):
        app_module = importlib.import_module("connect_ai.app")
        app = app_module.app

        with app.test_client() as client:
            response = client.get("/metrics")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"# HELP", response.data)


if __name__ == "__main__":
    unittest.main()
