import os
import sys
import time
from pathlib import Path

from flask import Flask, Response, request
from flask_login import LoginManager

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[1]
for path in [str(PROJECT_ROOT), str(BASE_DIR)]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from config import Config
from db import db
from models import User
from observability import (
    build_metrics_text,
    configure_telemetry,
    end_request_span,
    publish_kafka_event,
    start_request_span,
)
from production import build_readiness_payload
from agent.multi_agents import ManagerAgent
from mlops import MLOpsManager

# -------------------------------
# Create Flask App
# -------------------------------
app = Flask(__name__)
app.config.from_object(Config)
app.config.setdefault("OTEL_ENABLED", os.getenv("OTEL_ENABLED", "false").lower() == "true")
app.config.setdefault("OTEL_SERVICE_NAME", os.getenv("OTEL_SERVICE_NAME", "connect-ai"))
app.config.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", ""))
app.config.setdefault("PROMETHEUS_ENABLED", os.getenv("PROMETHEUS_ENABLED", "true").lower() != "false")
app.config.setdefault("KAFKA_ENABLED", os.getenv("KAFKA_ENABLED", "false").lower() == "true")
app.config.setdefault("HEALTHCHECK_PATH", os.getenv("HEALTHCHECK_PATH", "/healthz"))

# -------------------------------
# Initialize Extensions
# -------------------------------
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@app.before_request
def before_request():
    if app.config.get("PROMETHEUS_ENABLED", True):
        request._start_time = time.time()
        request._span = start_request_span(app, request)


@app.after_request
def after_request(response):
    if app.config.get("PROMETHEUS_ENABLED", True):
        elapsed = time.time() - getattr(request, "_start_time", time.time())
        from observability import REQUEST_COUNTERS, REQUEST_LATENCY_COUNT, REQUEST_LATENCY_SUM

        path = request.path or "/"
        REQUEST_COUNTERS[(request.method, path, response.status_code)] += 1
        REQUEST_LATENCY_SUM[(request.method, path)] += elapsed
        REQUEST_LATENCY_COUNT[(request.method, path)] += 1

        end_request_span(getattr(request, "_span", None), response)

    if app.config.get("KAFKA_ENABLED", False):
        publish_kafka_event("http_request", {"path": request.path, "method": request.method, "status": response.status_code})

    return response


@app.route(app.config.get("HEALTHCHECK_PATH", "/healthz"))
def healthcheck():
    return {"status": "ok"}, 200


@app.route("/metrics")
def metrics():
    if not app.config.get("PROMETHEUS_ENABLED", True):
        return Response("", status=404, mimetype="text/plain")
    return Response(build_metrics_text(), mimetype="text/plain")


@app.route("/ready")
def ready():
    return build_readiness_payload(), 200


multi_agent_manager = ManagerAgent()


@app.route("/multi-agent", methods=["POST"])
def multi_agent():
    payload = request.get_json(silent=True) or {}
    text = payload.get("message") or payload.get("text") or ""
    result = multi_agent_manager.dispatch(text)
    return {"result": result}, 200


@app.route("/mlops")
def mlops_status():
    manager = MLOpsManager()
    run = manager.start_run("app-start")
    manager.log_metric(run["run_id"], "requests_seen", 1)
    manager.log_param(run["run_id"], "environment", "development")
    return {"status": "ok", "run": run}, 200


# -------------------------------
# User Loader for LoginManager
# -------------------------------
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# -------------------------------
# Register Blueprints
# -------------------------------
from routes.auth import auth
from routes.main import main
from routes.messages import messages
from routes.ai import ai

app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(messages)
app.register_blueprint(ai)


# -------------------------------
# Create Database Tables
# -------------------------------
with app.app_context():
    db.create_all()

configure_telemetry(app)


# -------------------------------
# Run Flask Server
# -------------------------------
if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("DEBUG", "true").lower() == "true"
    )