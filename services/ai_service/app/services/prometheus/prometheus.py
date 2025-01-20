from contextlib import asynccontextmanager
from typing import Literal
from prometheus_client import Counter, Histogram, Gauge
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import psutil
import time

# Request metrics (existing)
request_count = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

request_latency = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

# System metrics
cpu_usage = Gauge("system_cpu_usage_percent", "Current CPU usage percentage")
memory_usage = Gauge(
    "system_memory_usage_bytes",
    "Current memory usage in bytes",
    ["type"],  # different memory metrics (total, available, used)
)

# Application-specific metrics
active_connections = Gauge(
    "app_active_connections", "Number of current active connections"
)

rabbitmq_messages = Counter(
    "rabbitmq_messages_total",
    "Total number of RabbitMQ messages processed",
    ["status"],  # success, error
)

elasticsearch_operations = Counter(
    "elasticsearch_operations_total",
    "Total number of Elasticsearch operations",
    ["operation", "status"],  # operation: search, index, delete, etc.
)

embedding_requests = Counter(
    "embedding_requests_total",
    "Total number of embedding requests to Azure AI",
    ["status"],
)

embedding_latency = Histogram(
    "embedding_request_duration_seconds",
    "Embedding request duration in seconds",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

# Queue metrics
queue_size = Gauge(
    "rabbitmq_queue_size",
    "Current number of messages in RabbitMQ queue",
    ["queue_name"],
)

# Error tracking
error_count = Counter(
    "application_errors_total",
    "Total number of application errors",
    ["type", "location"],
)

# Dependency health
dependency_health = Gauge(
    "dependency_health",
    "Health status of dependencies (1 for healthy, 0 for unhealthy)",
    ["service"],
)

# Chat-specific metrics
chat_requests = Counter(
    "chat_requests_total",
    "Total number of chat requests processed",
    ["status"],  # success, error
)

chat_response_time = Histogram(
    "chat_response_time_seconds",
    "Time taken to generate chat responses",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0],
)

embedding_generation_requests = Counter(
    "embedding_generation_requests_total",
    "Total number of embedding generation requests",
    ["status"],  # success, error
)

embedding_generation_time = Histogram(
    "embedding_generation_time_seconds",
    "Time taken to generate embeddings",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

embedding_vector_size = Histogram(
    "embedding_vector_size_bytes",
    "Size of generated embedding vectors",
    buckets=[1024, 2048, 4096, 8192, 16384],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        # Initialize memory usage metrics
        self.update_system_metrics()

    def update_system_metrics(self) -> None:
        """Update system-level metrics"""
        cpu_usage.set(psutil.cpu_percent())
        mem = psutil.virtual_memory()
        memory_usage.labels(type="total").set(mem.total)
        memory_usage.labels(type="available").set(mem.available)
        memory_usage.labels(type="used").set(mem.used)

    def track_rabbitmq_message(self, status: Literal["success", "error"]) -> None:
        """Track RabbitMQ message processing"""
        rabbitmq_messages.labels(status=status).inc()

    def track_elasticsearch_operation(
        self,
        operation: Literal["search", "index", "delete", "update", "bulk"],
        status: Literal["success", "error"],
    ) -> None:
        """Track Elasticsearch operations"""
        elasticsearch_operations.labels(operation=operation, status=status).inc()

    def track_embedding_generation(
        self, status: Literal["success", "error"], vector_size: int | None = None
    ) -> None:
        """Track embedding generation metrics"""
        embedding_generation_requests.labels(status=status).inc()
        if vector_size and status == "success":
            embedding_vector_size.observe(vector_size)

    def update_queue_size(self, queue_name: str, size: int) -> None:
        """Update RabbitMQ queue size"""
        queue_size.labels(queue_name=queue_name).set(size)

    def track_error(self, error_type: str, location: str) -> None:
        """Track application errors"""
        error_count.labels(type=error_type, location=location).inc()

    def update_dependency_health(
        self,
        service: Literal["rabbitmq", "elasticsearch", "azure_ai"],
        is_healthy: bool,
    ) -> None:
        """Update dependency health status"""
        dependency_health.labels(service=service).set(1 if is_healthy else 0)

    def track_embedding_request(
        self, status: Literal["success", "error"], duration: float
    ) -> None:
        """Track embedding request metrics"""
        embedding_requests.labels(status=status).inc()
        embedding_latency.observe(duration)

    def track_chat_request(self, status: Literal["success", "error"]) -> None:
        """Track chat request outcomes"""
        chat_requests.labels(status=status).inc()

    @asynccontextmanager
    async def track_async_operation(
        self,
        operation_type: Literal[
            "rabbitmq", "elasticsearch", "embedding", "health_check"
        ],
        operation: str | None = None,
        queue_name: str | None = None,
    ):
        start_time = time.time()
        try:
            yield
            duration = time.time() - start_time

            if operation_type == "embedding":
                if operation == "generation":
                    # Track embedding generation metrics
                    embedding_generation_time.observe(duration)
                    self.track_embedding_generation("success")
                elif operation == "chat_generation":
                    # Track chat-specific metrics
                    chat_response_time.observe(duration)
                    self.track_chat_request("success")
                # Track general embedding request
                self.track_embedding_request("success", duration)

            elif operation_type == "elasticsearch":
                if operation:
                    self.track_elasticsearch_operation(operation, "success")

            elif operation_type == "rabbitmq":
                self.track_rabbitmq_message("success")
                if queue_name:
                    #  TODO: and update the queue size
                    pass

        except Exception as e:
            if operation_type == "embedding":
                if operation == "generation":
                    self.track_embedding_generation("error")
                elif operation == "chat_generation":
                    self.track_chat_request("error")
                self.track_embedding_request("error", time.time() - start_time)

            elif operation_type == "elasticsearch" and operation:
                self.track_elasticsearch_operation(operation, "error")
            elif operation_type == "rabbitmq":
                self.track_rabbitmq_message("error")

            self.track_error(type(e).__name__, operation_type)
            raise

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Update active connections
        active_connections.inc()

        try:
            # Measure request duration
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time

            # Update request metrics
            request_count.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
            ).inc()

            request_latency.labels(
                method=request.method, endpoint=request.url.path
            ).observe(duration)

            return response
        except Exception as e:
            # Track errors
            self.track_error(error_type=type(e).__name__, location=request.url.path)
            raise
        finally:
            active_connections.dec()
