import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class MLOpsManager:
    def __init__(self, tracking_uri: Optional[str] = None, experiment_name: Optional[str] = None):
        self.tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")
        self.experiment_name = experiment_name or os.getenv("MLFLOW_EXPERIMENT_NAME", "connect-ai")
        self.run_dir = Path(os.getenv("MLOPS_RUN_DIR", "./mlruns"))
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def start_run(self, run_name: Optional[str] = None) -> Dict[str, Any]:
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        run_id = f"{(run_name or 'run').replace(' ', '-')}-{timestamp}"
        metadata = {
            "run_id": run_id,
            "experiment_name": self.experiment_name,
            "tracking_uri": self.tracking_uri,
            "started_at": datetime.utcnow().isoformat(),
        }
        self._write_json(self.run_dir / f"{run_id}.json", metadata)
        return metadata

    def log_metric(self, run_id: str, key: str, value: float) -> Dict[str, Any]:
        payload = {"run_id": run_id, "key": key, "value": value, "logged_at": datetime.utcnow().isoformat()}
        self._write_json(self.run_dir / f"{run_id}-{key}.json", payload)
        return payload

    def log_param(self, run_id: str, key: str, value: Any) -> Dict[str, Any]:
        payload = {"run_id": run_id, "key": key, "value": value, "logged_at": datetime.utcnow().isoformat()}
        self._write_json(self.run_dir / f"{run_id}-{key}.json", payload)
        return payload

    def register_model(self, run_id: str, model_name: str, stage: str = "staging") -> Dict[str, Any]:
        payload = {
            "run_id": run_id,
            "model_name": model_name,
            "stage": stage,
            "registered_at": datetime.utcnow().isoformat(),
        }
        self._write_json(self.run_dir / f"{model_name}-{run_id}.json", payload)
        return payload

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, default=str)
