import socket
import time
from dataclasses import dataclass
from typing import Callable

import requests


@dataclass(frozen=True)
class ReadinessCheck:
    name: str
    probe: Callable[[], bool]


def wait_for_checks(checks: list[ReadinessCheck], timeout_seconds: int = 180, interval_seconds: float = 2.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    remaining = {check.name: check for check in checks}
    failures: dict[str, int] = {check.name: 0 for check in checks}

    while remaining:
        for name, check in list(remaining.items()):
            if check.probe():
                remaining.pop(name, None)
                continue
            failures[name] += 1

        if not remaining:
            return
        if time.monotonic() >= deadline:
            failed_names = ", ".join(f"{name}({count} misses)" for name, count in failures.items() if name in remaining)
            raise TimeoutError(f"Smoke readiness checks did not pass before timeout: {failed_names}")
        time.sleep(interval_seconds)


def http_get_check(url: str, expected_status: int = 200, timeout_seconds: float = 5.0) -> ReadinessCheck:
    def probe() -> bool:
        try:
            response = requests.get(url, timeout=timeout_seconds)
            return response.status_code == expected_status
        except requests.RequestException:
            return False

    return ReadinessCheck(name=url, probe=probe)


def tcp_check(host: str, port: int, timeout_seconds: float = 2.0) -> ReadinessCheck:
    def probe() -> bool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_seconds)
        try:
            sock.connect((host, port))
            return True
        except OSError:
            return False
        finally:
            sock.close()

    return ReadinessCheck(name=f"tcp://{host}:{port}", probe=probe)
