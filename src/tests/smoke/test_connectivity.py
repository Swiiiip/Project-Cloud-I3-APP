import socket

import requests

from src.tests.smoke.config import SmokeConfig
from src.tests.smoke.result_types import ScenarioResult


def _tcp_connect(host: str, port: int, timeout: float = 3.0) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def run(config: SmokeConfig) -> ScenarioResult:
    checks: list[tuple[str, bool]] = []

    if config.game_state_storage_host and config.game_state_storage_port is not None:
        checks.append(("game_state_storage_tcp", _tcp_connect(config.game_state_storage_host, config.game_state_storage_port)))

    gateway_health = requests.get(f"{config.gateway_base_url}/health", timeout=30)
    checks.append(("gateway_health", gateway_health.status_code == 200))

    if config.game_engine_service_base_url:
        game_engine_health = requests.get(f"{config.game_engine_service_base_url}/internal/game_engine/health", timeout=30)
        checks.append(("game_engine_health", game_engine_health.status_code == 200))

    if config.emoji_catalog_service_base_url:
        emoji_catalog_health = requests.get(f"{config.emoji_catalog_service_base_url}/internal/emoji_catalog/health", timeout=30)
        checks.append(("emoji_catalog_health", emoji_catalog_health.status_code == 200))

    if config.emoji_render_service_base_url:
        emoji_render_health = requests.get(f"{config.emoji_render_service_base_url}/internal/emoji_render/health", timeout=30)
        checks.append(("emoji_render_health", emoji_render_health.status_code == 200))

    passed = all(ok for _, ok in checks)
    details = ", ".join(f"{name}={ok}" for name, ok in checks)

    return ScenarioResult(name="connectivity", passed=passed, details=details)


if __name__ == "__main__":
    result = run(SmokeConfig.from_env())
    print(result)
    raise SystemExit(0 if result.passed else 1)


