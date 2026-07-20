import os
from pathlib import Path

from connect_ai.mlops import MLOpsManager


if __name__ == "__main__":
    manager = MLOpsManager()
    run = manager.start_run("training-demo")
    manager.log_param(run["run_id"], "dataset", "demo")
    manager.log_metric(run["run_id"], "accuracy", 0.92)
    manager.register_model(run["run_id"], "connect-ai-model")
    print(run)
