import argparse

from src.tests.smoke.config import SmokeConfig
from src.tests.smoke.result_types import ScenarioResult
from src.tests.smoke.wait import http_get_check, tcp_check, wait_for_checks
from src.tests.smoke.test_concurrent_sessions import run as run_concurrent_sessions
from src.tests.smoke.test_connectivity import run as run_connectivity
from src.tests.smoke.test_gateway_restrictions import run as run_gateway_restrictions
from src.tests.smoke.test_queue_delay import run as run_queue_delay
from src.tests.smoke.test_stress import run as run_stress

SCENARIOS = {
    "queue_delay": run_queue_delay,
    "concurrent_sessions": run_concurrent_sessions,
    "gateway_restrictions": run_gateway_restrictions,
    "stress": run_stress,
    "connectivity": run_connectivity,
}


def _wait_for_scenario_targets(config: SmokeConfig, selected: list[str]) -> None:
    readiness_checks = [http_get_check(f"{config.gateway_base_url}/health")]

    if config.game_service_base_url:
        readiness_checks.append(http_get_check(f"{config.game_service_base_url}/internal/game/health"))

    if config.catalog_service_base_url:
        readiness_checks.append(http_get_check(f"{config.catalog_service_base_url}/internal/catalog/health"))

    if config.render_service_base_url:
        readiness_checks.append(http_get_check(f"{config.render_service_base_url}/internal/render/health"))

    if "gateway_restrictions" in selected:
        readiness_checks.append(http_get_check(f"{config.frontend_base_url}/"))

    if "connectivity" in selected:
        if config.redis_host and config.redis_port is not None:
            readiness_checks.append(tcp_check(config.redis_host, config.redis_port))

    wait_for_checks(readiness_checks, timeout_seconds=180, interval_seconds=2.0)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Blurmoji split-service smoke tests")
    parser.add_argument(
        "--scenario",
        action="append",
        choices=sorted(SCENARIOS.keys()),
        help="Run only selected scenario(s). Can be repeated.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    config = SmokeConfig.from_env()

    selected = args.scenario or list(SCENARIOS.keys())

    _wait_for_scenario_targets(config, selected)

    results: list[ScenarioResult] = []
    for scenario_name in selected:
        scenario_runner = SCENARIOS[scenario_name]
        result = scenario_runner(config)
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}: {result.details}")

    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

