import requests

from src.tests.smoke.config import SmokeConfig
from src.tests.smoke.result_types import ScenarioResult


def run(config: SmokeConfig) -> ScenarioResult:
    public_session = requests.Session()

    gateway_start = public_session.get(f"{config.public_base_url}/api/v1/daily/start", timeout=30)
    gateway_open = gateway_start.status_code == 200

    restricted_paths = (
        "/internal/game_engine/health",
        "/internal/emoji_catalog/health",
        "/internal/emoji_render/health",
    )
    restricted_visible = []
    for path in restricted_paths:
        response = public_session.get(f"{config.public_base_url}{path}", timeout=30)
        restricted_visible.append(response.status_code == 200)

    frontend_api_open = False
    if config.frontend_base_url:
        frontend_response = public_session.get(f"{config.frontend_base_url}/api/v1/daily/start", timeout=30)
        frontend_api_open = frontend_response.status_code == 200

    passed = gateway_open and not any(restricted_visible) and not frontend_api_open

    details = (
        f"gateway_open={gateway_open} restricted_visible={restricted_visible} "
        f"frontend_api_open={frontend_api_open}"
    )

    return ScenarioResult(name="gateway_restrictions", passed=passed, details=details)


if __name__ == "__main__":
    result = run(SmokeConfig.from_env())
    print(result)
    raise SystemExit(0 if result.passed else 1)

