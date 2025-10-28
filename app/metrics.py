"""Prometheus metrics for API monitoring."""
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator, metrics

# Custom metrics
REQUESTS_TOTAL = Counter(
    "api_requests_total",
    "Total requests by endpoint and status",
    ["endpoint", "status"]
)

LATENCY_SECONDS = Histogram(
    "api_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

MODEL_ERRORS = Counter(
    "model_errors_total",
    "Total model errors by type",
    ["model", "error_type"]
)

SAFETY_BLOCKS = Counter(
    "safety_blocks_total",
    "Content blocked by safety rules",
    ["rule_type"]
)

RATE_LIMITS = Counter(
    "rate_limits_total",
    "Rate limit hits by API key",
    ["api_key_hash"]  # Hash the key for privacy
)

ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active connections"
)

def init_metrics(app):
    """Initialize Prometheus metrics and FastAPI instrumentation."""
    
    # Add default FastAPI metrics
    instrumentator = Instrumentator().instrument(app)
    
    # Add custom metrics for response time
    instrumentator.add(metrics.latency())
    
    # Add custom metrics for request size
    instrumentator.add(metrics.request_size())
    
    # Initialize instrumentation
    instrumentator.expose(app, include_in_schema=True, should_gzip=True)