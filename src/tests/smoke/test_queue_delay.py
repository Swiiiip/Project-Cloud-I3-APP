import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.tests.smoke.config import SmokeConfig
from src.tests.smoke.http_client import GatewaySmokeClient
from src.tests.smoke.result_types import ScenarioResult


def run(config: SmokeConfig) -> ScenarioResult:
    client = GatewaySmokeClient(config.gateway_base_url)

    sessions = [client.new_session() for _ in range(config.queue_concurrency)]
    session_ids: list[str] = []
    for session in sessions:
        start_response = client.start(session)
        start_response.raise_for_status()
        session_id = session.cookies.get("session_id")
        if not session_id:
            raise ValueError("Queue delay smoke test expected a session cookie after /start")
        session_ids.append(session_id)

    durations: list[float] = []

    def render_once(session_index: int) -> float:
        started_at = time.perf_counter()
        session = client.new_session()
        session.cookies.set("session_id", session_ids[session_index], path="/")
        response = client.render(session)
        response.raise_for_status()
        return time.perf_counter() - started_at

    futures = []
    with ThreadPoolExecutor(max_workers=config.queue_concurrency) as executor:
        for _ in range(config.queue_iterations_per_user):
            for index in range(config.queue_concurrency):
                futures.append(executor.submit(render_once, index))

        for future in as_completed(futures):
            durations.append(future.result())

    max_delay = max(durations) if durations else 0.0
    p95_delay = statistics.quantiles(durations, n=100)[94] if len(durations) >= 100 else max_delay
    passed = max_delay >= config.queue_delay_threshold_seconds

    details = (
        f"requests={len(durations)} max_delay={max_delay:.3f}s "
        f"p95_delay={p95_delay:.3f}s threshold={config.queue_delay_threshold_seconds:.3f}s"
    )
    if not passed:
        details = f"Queue delay threshold was not reached. {details}"

    return ScenarioResult(name="queue_delay", passed=passed, details=details)


if __name__ == "__main__":
    result = run(SmokeConfig.from_env())
    print(result)
    raise SystemExit(0 if result.passed else 1)

