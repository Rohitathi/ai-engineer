import os
from typing import Any, Dict


def build_readiness_payload() -> Dict[str, Any]:
    return {
        "redis": {
            "enabled": os.getenv("REDIS_ENABLED", "false").lower() == "true",
            "url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        },
        "kafka": {
            "enabled": os.getenv("KAFKA_ENABLED", "false").lower() == "true",
            "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        },
        "mlops": {
            "enabled": os.getenv("MLOPS_ENABLED", "false").lower() == "true",
            "tracking_uri": os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001"),
        },
        "github_sync": {
            "enabled": os.getenv("GITHUB_SYNC_ENABLED", "false").lower() == "true",
            "repo": os.getenv("GITHUB_REPO", ""),
        },
    }
