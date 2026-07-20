import os


def build_mlops_config() -> dict:
    return {
        "enabled": os.getenv("MLOPS_ENABLED", "false").lower() == "true",
        "tracking_uri": os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001"),
    }
