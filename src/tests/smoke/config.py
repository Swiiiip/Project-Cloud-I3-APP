import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SmokeConfig:
    gateway_base_url: str
    frontend_base_url: str
    public_base_url: str
    game_engine_service_base_url: str
    emoji_catalog_service_base_url: str
    emoji_render_service_base_url: str
    queue_concurrency: int
    queue_iterations_per_user: int
    queue_delay_threshold_seconds: float
    concurrent_session_count: int
    stress_total_requests: int
    stress_concurrency: int
    stress_max_error_rate: float
    stress_p95_max_seconds: float
    game_state_storage_host: str
    game_state_storage_port: int | None

    @staticmethod
    def from_env() -> "SmokeConfig":
        def require_env(key: str) -> str:
            value = os.getenv(key)
            if value is None or not value.strip():
                raise ValueError(f"Missing required smoke test environment variable '{key}'")
            return value.strip()

        def optional_env(key: str) -> str:
            value = os.getenv(key)
            return value.strip() if value and value.strip() else ""

        def first_optional_env(*keys: str) -> str:
            for key in keys:
                value = optional_env(key)
                if value:
                    return value
            return ""

        def first_optional_int_env(*keys: str) -> int | None:
            value = first_optional_env(*keys)
            if not value:
                return None
            return int(value)

        return SmokeConfig(
            gateway_base_url=require_env("SMOKE_GATEWAY_BASE_URL").rstrip("/"),
            frontend_base_url=require_env("SMOKE_FRONTEND_BASE_URL").rstrip("/"),
            public_base_url=require_env("SMOKE_PUBLIC_BASE_URL").rstrip("/"),
            game_engine_service_base_url=first_optional_env(
                "SMOKE_GAME_ENGINE_SERVICE_BASE_URL", "SMOKE_GAME_SERVICE_BASE_URL"
            ).rstrip("/"),
            emoji_catalog_service_base_url=first_optional_env(
                "SMOKE_EMOJI_CATALOG_SERVICE_BASE_URL", "SMOKE_CATALOG_SERVICE_BASE_URL"
            ).rstrip("/"),
            emoji_render_service_base_url=first_optional_env(
                "SMOKE_EMOJI_RENDER_SERVICE_BASE_URL", "SMOKE_RENDER_SERVICE_BASE_URL"
            ).rstrip("/"),
            queue_concurrency=int(require_env("SMOKE_QUEUE_CONCURRENCY")),
            queue_iterations_per_user=int(require_env("SMOKE_QUEUE_ITERATIONS_PER_USER")),
            queue_delay_threshold_seconds=float(require_env("SMOKE_QUEUE_DELAY_THRESHOLD_SECONDS")),
            concurrent_session_count=int(require_env("SMOKE_CONCURRENT_SESSION_COUNT")),
            stress_total_requests=int(require_env("SMOKE_STRESS_TOTAL_REQUESTS")),
            stress_concurrency=int(require_env("SMOKE_STRESS_CONCURRENCY")),
            stress_max_error_rate=float(require_env("SMOKE_STRESS_MAX_ERROR_RATE")),
            stress_p95_max_seconds=float(require_env("SMOKE_STRESS_P95_MAX_SECONDS")),
            game_state_storage_host=first_optional_env("SMOKE_GAME_STATE_STORAGE_HOST", "SMOKE_REDIS_HOST"),
            game_state_storage_port=first_optional_int_env("SMOKE_GAME_STATE_STORAGE_PORT", "SMOKE_REDIS_PORT"),
        )
