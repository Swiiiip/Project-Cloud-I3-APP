import json
import os
import threading
import time
import uuid
from contextlib import contextmanager
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import cast

_STATE_BY_SESSION: dict[str, dict] = {}
_LOCK = threading.Lock()


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict, cookie: str | None = None) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    if cookie is not None:
        handler.send_header("Set-Cookie", f"session_id={cookie}; Path=/")
    handler.end_headers()
    handler.wfile.write(body)


def _png_response(handler: BaseHTTPRequestHandler) -> None:
    # 1x1 PNG payload to emulate render output.
    body = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", "image/png")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _extract_session_id(handler: BaseHTTPRequestHandler) -> str | None:
    cookie_header = handler.headers.get("Cookie", "")
    for token in cookie_header.split(";"):
        item = token.strip()
        if item.startswith("session_id="):
            return item.split("=", 1)[1]
    return None


class MockGatewayHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            _json_response(self, HTTPStatus.OK, {"status": "ok"})
            return

        if self.path.startswith("/api/v1/daily/start"):
            session_id = _extract_session_id(self)
            if session_id is None:
                session_id = str(uuid.uuid4())
            with _LOCK:
                _STATE_BY_SESSION.setdefault(
                    session_id,
                    {
                        "attempts": 0,
                        "past_guesses": [],
                        "past_guess_matches": [],
                    },
                )
            _json_response(
                self,
                HTTPStatus.OK,
                {
                    "attempts": 0,
                    "max_attempts": 5,
                    "is_completed": False,
                    "answer": {
                        "name": "mock",
                        "emoji_codepoint_couple": {
                            "first_emoji_codepoint": "1f600",
                            "second_emoji_codepoint": "1f602",
                        },
                        "result_image_url": "http://example.local/result.png",
                    },
                    "past_guesses": [],
                    "past_guess_matches": [],
                },
                cookie=session_id,
            )
            return

        if self.path.startswith("/api/v1/daily/get_status"):
            session_id = _extract_session_id(self)
            if session_id is None:
                _json_response(self, HTTPStatus.FORBIDDEN, {"detail": "No active session found"})
                return
            with _LOCK:
                state = _STATE_BY_SESSION.get(session_id)
            if state is None:
                _json_response(self, HTTPStatus.FORBIDDEN, {"detail": "No active session found"})
                return
            _json_response(
                self,
                HTTPStatus.OK,
                {
                    "attempts": state["attempts"],
                    "max_attempts": 5,
                    "is_completed": False,
                    "answer": {
                        "name": "mock",
                        "emoji_codepoint_couple": {
                            "first_emoji_codepoint": "1f600",
                            "second_emoji_codepoint": "1f602",
                        },
                        "result_image_url": "http://example.local/result.png",
                    },
                    "past_guesses": state["past_guesses"],
                    "past_guess_matches": state["past_guess_matches"],
                },
            )
            return

        if self.path.startswith("/api/v1/daily/supported_emojis"):
            _json_response(
                self,
                HTTPStatus.OK,
                {
                    "categories": [
                        {
                            "category": "mock",
                            "emojis": [
                                {"codepoint": "1f600", "keyboardPosition": 1},
                                {"codepoint": "1f602", "keyboardPosition": 2},
                            ],
                        }
                    ]
                },
            )
            return

        if self.path.startswith("/api/v1/daily/render"):
            time.sleep(2.1)
            _png_response(self)
            return

        _json_response(self, HTTPStatus.NOT_FOUND, {"detail": "not found"})

    def do_POST(self) -> None:
        if not self.path.startswith("/api/v1/daily/guess"):
            _json_response(self, HTTPStatus.NOT_FOUND, {"detail": "not found"})
            return

        session_id = _extract_session_id(self)
        if session_id is None:
            _json_response(self, HTTPStatus.FORBIDDEN, {"detail": "No active session found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}

        with _LOCK:
            state = _STATE_BY_SESSION.setdefault(
                session_id,
                {"attempts": 0, "past_guesses": [], "past_guess_matches": []},
            )
            state["attempts"] += 1
            state["past_guesses"].append(
                {
                    "first_emoji": {"codepoint": payload.get("first_emoji_codepoint", "1f600")},
                    "second_emoji": {"codepoint": payload.get("second_emoji_codepoint", "1f602")},
                }
            )
            state["past_guess_matches"].append(
                {
                    "first_slot_match": False,
                    "second_slot_match": False,
                }
            )

        _json_response(
            self,
            HTTPStatus.OK,
            {
                "attempts": state["attempts"],
                "max_attempts": 5,
                "is_completed": False,
                "answer": {
                    "name": "mock",
                    "emoji_codepoint_couple": {
                        "first_emoji_codepoint": "1f600",
                        "second_emoji_codepoint": "1f602",
                    },
                    "result_image_url": "http://example.local/result.png",
                },
                "past_guesses": state["past_guesses"],
                "past_guess_matches": state["past_guess_matches"],
            },
        )

    def log_message(self, format: str, *args) -> None:
        return


@contextmanager
def run_mock_gateway(host: str = "127.0.0.1", port: int = 18080):
    server = ThreadingHTTPServer((host, port), cast(type[BaseHTTPRequestHandler], MockGatewayHandler))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=2)


def main() -> int:
    from src.tests.smoke.run_suite import main as run_suite_main

    with run_mock_gateway() as base_url:
        os.environ["SMOKE_GATEWAY_BASE_URL"] = base_url
        os.environ["SMOKE_PUBLIC_BASE_URL"] = base_url
        os.environ["SMOKE_FRONTEND_BASE_URL"] = f"{base_url}/frontend"
        os.environ["SMOKE_QUEUE_DELAY_THRESHOLD_SECONDS"] = "2.0"
        os.environ["SMOKE_QUEUE_CONCURRENCY"] = "8"
        os.environ["SMOKE_QUEUE_ITERATIONS_PER_USER"] = "2"
        os.environ["SMOKE_CONCURRENT_SESSION_COUNT"] = "16"
        os.environ["SMOKE_STRESS_TOTAL_REQUESTS"] = "80"
        os.environ["SMOKE_STRESS_CONCURRENCY"] = "8"
        os.environ["SMOKE_STRESS_MAX_ERROR_RATE"] = "0.03"
        os.environ["SMOKE_STRESS_P95_MAX_SECONDS"] = "3.0"
        os.environ["SMOKE_GAME_STATE_STORAGE_PORT"] = "6379"

        import sys

        sys.argv = [
            sys.argv[0],
            "--scenario",
            "queue_delay",
            "--scenario",
            "concurrent_sessions",
            "--scenario",
            "gateway_restrictions",
            "--scenario",
            "stress",
        ]
        return run_suite_main()


if __name__ == "__main__":
    raise SystemExit(main())

