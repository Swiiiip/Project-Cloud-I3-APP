import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SmokeConfig:
    gateway_base_url: str
    frontend_base_url: str
    public_base_url: str
    game_service_base_url: str
    catalog_service_base_url: str
    render_service_base_url: str
    queue_concurrency: int
    queue_iterations_per_user: int
    queue_delay_threshold_seconds: float
    concurrent_session_count: int
    stress_total_requests: int
    stress_concurrency: int
    stress_max_error_rate: float
    stress_p95_max_seconds: float
    redis_host: str
    redis_port: int
    mysql_host: str
    mysql_port: int
    azurite_host: str
    azurite_port: int

    @staticmethod
    def from_env() -> "SmokeConfig":
        return SmokeConfig(
            gateway_base_url=os.getenv("SMOKE_GATEWAY_BASE_URL", "http://localhost:8000").rstrip("/"),
            frontend_base_url=os.getenv("SMOKE_FRONTEND_BASE_URL", "http://localhost:8001").rstrip("/"),
            public_base_url=os.getenv("SMOKE_PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/"),
            game_service_base_url=os.getenv("SMOKE_GAME_SERVICE_BASE_URL", "").rstrip("/"),
            catalog_service_base_url=os.getenv("SMOKE_CATALOG_SERVICE_BASE_URL", "").rstrip("/"),
            render_service_base_url=os.getenv("SMOKE_RENDER_SERVICE_BASE_URL", "").rstrip("/"),
            queue_concurrency=int(os.getenv("SMOKE_QUEUE_CONCURRENCY", "40")),
            queue_iterations_per_user=int(os.getenv("SMOKE_QUEUE_ITERATIONS_PER_USER", "4")),
            queue_delay_threshold_seconds=float(os.getenv("SMOKE_QUEUE_DELAY_THRESHOLD_SECONDS", "2.0")),
            concurrent_session_count=int(os.getenv("SMOKE_CONCURRENT_SESSION_COUNT", "100")),
            stress_total_requests=int(os.getenv("SMOKE_STRESS_TOTAL_REQUESTS", "500")),
            stress_concurrency=int(os.getenv("SMOKE_STRESS_CONCURRENCY", "40")),
            stress_max_error_rate=float(os.getenv("SMOKE_STRESS_MAX_ERROR_RATE", "0.03")),
            stress_p95_max_seconds=float(os.getenv("SMOKE_STRESS_P95_MAX_SECONDS", "2.0")),
            redis_host=os.getenv("SMOKE_REDIS_HOST", os.getenv("REDIS_HOST", "localhost")),
            redis_port=int(os.getenv("SMOKE_REDIS_PORT", os.getenv("REDIS_PORT", "6379"))),
            mysql_host=os.getenv("SMOKE_MYSQL_HOST", "localhost"),
            mysql_port=int(os.getenv("SMOKE_MYSQL_PORT", "3306")),
            azurite_host=os.getenv("SMOKE_AZURITE_HOST", "localhost"),
            azurite_port=int(os.getenv("SMOKE_AZURITE_PORT", "10000")),
        )

