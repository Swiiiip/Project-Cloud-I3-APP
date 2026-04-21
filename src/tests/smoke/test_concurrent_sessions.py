from concurrent.futures import ThreadPoolExecutor, as_completed

from src.tests.smoke.config import SmokeConfig
from src.tests.smoke.http_client import GatewaySmokeClient, extract_two_codepoints_from_supported_payload
from src.tests.smoke.result_types import ScenarioResult


def run(config: SmokeConfig) -> ScenarioResult:
    client = GatewaySmokeClient(config.gateway_base_url)

    probe_session = client.new_session()
    supported_response = client.supported_emojis(probe_session)
    supported_response.raise_for_status()
    first_codepoint, second_codepoint = extract_two_codepoints_from_supported_payload(supported_response.json())

    def run_for_user(_: int) -> tuple[str, int, int, int]:
        session = client.new_session()

        start_response = client.start(session)
        start_response.raise_for_status()

        guess_response = client.guess(session, first_codepoint, second_codepoint)
        guess_response.raise_for_status()

        status_response = client.status(session)
        status_response.raise_for_status()
        state = status_response.json()

        cookie_value = session.cookies.get("session_id") or ""
        attempts = int(state.get("attempts", -1))
        guesses_count = len(state.get("past_guesses", []))
        matches_count = len(state.get("past_guess_matches", []))
        return cookie_value, attempts, guesses_count, matches_count

    session_rows: list[tuple[str, int, int, int]] = []
    with ThreadPoolExecutor(max_workers=min(config.concurrent_session_count, 64)) as executor:
        futures = [executor.submit(run_for_user, index) for index in range(config.concurrent_session_count)]
        for future in as_completed(futures):
            session_rows.append(future.result())

    session_ids = [row[0] for row in session_rows]
    unique_sessions = len(set(session_ids))
    no_blank_sessions = all(bool(value) for value in session_ids)
    attempts_ok = all(row[1] == 1 for row in session_rows)
    guesses_ok = all(row[2] == 1 for row in session_rows)
    matches_ok = all(row[3] == 1 for row in session_rows)

    passed = (
        unique_sessions == config.concurrent_session_count
        and no_blank_sessions
        and attempts_ok
        and guesses_ok
        and matches_ok
    )

    details = (
        f"sessions={config.concurrent_session_count} unique_sessions={unique_sessions} "
        f"attempts_ok={attempts_ok} guesses_ok={guesses_ok} matches_ok={matches_ok}"
    )

    return ScenarioResult(name="concurrent_sessions", passed=passed, details=details)


if __name__ == "__main__":
    result = run(SmokeConfig.from_env())
    print(result)
    raise SystemExit(0 if result.passed else 1)


