import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from src.tests.smoke.config import SmokeConfig
from src.tests.smoke.http_client import GatewaySmokeClient, extract_two_codepoints_from_supported_payload
from src.tests.smoke.result_types import ScenarioResult


def run(config: SmokeConfig) -> ScenarioResult:
    client = GatewaySmokeClient(config.gateway_base_url)
    bootstrap_session = client.new_session()

    supported_response = client.supported_emojis(bootstrap_session)
    supported_response.raise_for_status()
    first_codepoint, second_codepoint = extract_two_codepoints_from_supported_payload(supported_response.json())

    cookie_pool: list[str] = []
    for _ in range(max(10, config.stress_concurrency // 2)):
        session = client.new_session()
        start_response = client.start(session)
        start_response.raise_for_status()
        cookie = session.cookies.get("session_id")
        if cookie:
            cookie_pool.append(cookie)

    if not cookie_pool:
        return ScenarioResult(name="stress", passed=False, details="No session cookie was created")

    durations: list[float] = []
    errors = 0

    def do_request(_: int) -> tuple[float, bool]:
        started_at = time.perf_counter()
        op = random.random()
        session = requests.Session()
        cookie = random.choice(cookie_pool)
        session.cookies.set("session_id", cookie, path="/")

        try:
            if op < 0.50:
                response = client.status(session)
            elif op < 0.80:
                response = client.render(session)
            elif op < 0.95:
                response = client.supported_emojis(session)
            else:
                response = client.guess(session, first_codepoint, second_codepoint)
            ok = 200 <= response.status_code < 300
            if not ok:
                return time.perf_counter() - started_at, False
            return time.perf_counter() - started_at, True
        except requests.RequestException:
            return time.perf_counter() - started_at, False

    with ThreadPoolExecutor(max_workers=config.stress_concurrency) as executor:
        futures = [executor.submit(do_request, idx) for idx in range(config.stress_total_requests)]
        for future in as_completed(futures):
            duration, ok = future.result()
            durations.append(duration)
            if not ok:
                errors += 1

    error_rate = errors / config.stress_total_requests
    p95 = statistics.quantiles(durations, n=100)[94] if len(durations) >= 100 else max(durations)

    passed = error_rate <= config.stress_max_error_rate and p95 <= config.stress_p95_max_seconds
    details = (
        f"requests={config.stress_total_requests} errors={errors} error_rate={error_rate:.4f} "
        f"p95={p95:.3f}s max_error_rate={config.stress_max_error_rate:.4f} "
        f"max_p95={config.stress_p95_max_seconds:.3f}s"
    )

    return ScenarioResult(name="stress", passed=passed, details=details)


if __name__ == "__main__":
    result = run(SmokeConfig.from_env())
    print(result)
    raise SystemExit(0 if result.passed else 1)

