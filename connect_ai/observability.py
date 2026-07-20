import json
import os
import time
from collections import defaultdict
from typing import Any, Dict, Tuple

try:
    from opentelemetry import trace
except ImportError:  # pragma: no cover
    trace = None


REQUEST_COUNTERS: Dict[Tuple[str, str, int], int] = defaultdict(int)
REQUEST_LATENCY_SUM: Dict[Tuple[str, str], float] = defaultdict(float)
REQUEST_LATENCY_COUNT: Dict[Tuple[str, str], int] = defaultdict(int)


def _safe_metric_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_metrics_text() -> str:
    lines = []
    lines.append("# HELP connect_ai_http_requests_total Total HTTP requests")
    lines.append("# TYPE connect_ai_http_requests_total counter")
    for (method, path, status), count in sorted(REQUEST_COUNTERS.items()):
        lines.append(
            f'connect_ai_http_requests_total{{method="{_safe_metric_label(method)}",path="{_safe_metric_label(path)}",status="{status}"}} {count}'
        )

    lines.append("# HELP connect_ai_http_request_duration_seconds Request latency in seconds")
    lines.append("# TYPE connect_ai_http_request_duration_seconds summary")
    for (method, path), total in sorted(REQUEST_LATENCY_SUM.items()):
        count = REQUEST_LATENCY_COUNT.get((method, path), 0)
        average = total / count if count else 0.0
        lines.append(
            f'connect_ai_http_request_duration_seconds{{method="{_safe_metric_label(method)}",path="{_safe_metric_label(path)}"}} {average}'
        )

    lines.append("# HELP connect_ai_up Application availability")
    lines.append("# TYPE connect_ai_up gauge")
    lines.append("connect_ai_up 1")
    return "\n".join(lines) + "\n"


def configure_telemetry(app) -> None:
    if not app.config.get("OTEL_ENABLED", False) or trace is None:
        return

    try:
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.sdk.resources import Resource
    except ImportError:  # pragma: no cover
        return

    resource = Resource.create({"service.name": app.config.get("OTEL_SERVICE_NAME", "connect-ai")})
    provider = TracerProvider(resource=resource)

    if app.config.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        except ImportError:  # pragma: no cover
            exporter = ConsoleSpanExporter()
        else:
            exporter = OTLPSpanExporter(endpoint=app.config["OTEL_EXPORTER_OTLP_ENDPOINT"])
    else:
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)


def start_request_span(app, request) -> Any:
    if not app.config.get("OTEL_ENABLED", False) or trace is None:
        return None

    tracer = trace.get_tracer(app.config.get("OTEL_SERVICE_NAME", "connect-ai"))
    span = tracer.start_span(request.path)
    span.set_attribute("http.method", request.method)
    span.set_attribute("http.path", request.path)
    span.set_attribute("http.route", request.path)
    return span


def end_request_span(span: Any, response) -> None:
    if span is None:
        return
    span.set_attribute("http.status_code", response.status_code)
    span.end()


def publish_kafka_event(event_type: str, payload: Dict[str, Any]) -> bool:
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "").strip()
    topic = os.getenv("KAFKA_TOPIC", "connect-ai-events").strip()
    if not bootstrap_servers or not topic:
        return False

    try:
        from kafka import KafkaProducer
    except ImportError:  # pragma: no cover
        return False

    try:
        producer = KafkaProducer(
            bootstrap_servers=[server.strip() for server in bootstrap_servers.split(",") if server.strip()],
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )
        producer.send(topic, {"event": event_type, "payload": payload})
        producer.flush()
        return True
    except Exception:  # pragma: no cover
        return False
