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

    checks.append(("redis_tcp", _tcp_connect(config.redis_host, config.redis_port)))
    checks.append(("mysql_tcp", _tcp_connect(config.mysql_host, config.mysql_port)))
    checks.append(("azurite_tcp", _tcp_connect(config.azurite_host, config.azurite_port)))

    gateway_health = requests.get(f"{config.gateway_base_url}/health", timeout=30)
    checks.append(("gateway_health", gateway_health.status_code == 200))

    if config.game_service_base_url:
        game_health = requests.get(f"{config.game_service_base_url}/internal/game/health", timeout=30)
        checks.append(("game_health", game_health.status_code == 200))

    if config.catalog_service_base_url:
        catalog_health = requests.get(f"{config.catalog_service_base_url}/internal/catalog/health", timeout=30)
        checks.append(("catalog_health", catalog_health.status_code == 200))

    if config.render_service_base_url:
        render_health = requests.get(f"{config.render_service_base_url}/internal/render/health", timeout=30)
        checks.append(("render_health", render_health.status_code == 200))

    passed = all(ok for _, ok in checks)
    details = ", ".join(f"{name}={ok}" for name, ok in checks)

    return ScenarioResult(name="connectivity", passed=passed, details=details)


if __name__ == "__main__":
    result = run(SmokeConfig.from_env())
    print(result)
    raise SystemExit(0 if result.passed else 1)


