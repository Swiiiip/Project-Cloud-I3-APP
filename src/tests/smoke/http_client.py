import requests


class GatewaySmokeClient:
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    def new_session(self) -> requests.Session:
        return requests.Session()

    def start(self, session: requests.Session) -> requests.Response:
        return session.get(f"{self._base_url}/api/v1/daily/start", timeout=30)

    def status(self, session: requests.Session) -> requests.Response:
        return session.get(f"{self._base_url}/api/v1/daily/get_status", timeout=30)

    def supported_emojis(self, session: requests.Session) -> requests.Response:
        return session.get(f"{self._base_url}/api/v1/daily/supported_emojis", timeout=30)

    def render(self, session: requests.Session) -> requests.Response:
        return session.get(f"{self._base_url}/api/v1/daily/render", timeout=30)

    def guess(self, session: requests.Session, first_codepoint: str, second_codepoint: str) -> requests.Response:
        return session.post(
            f"{self._base_url}/api/v1/daily/guess",
            json={
                "first_emoji_codepoint": first_codepoint,
                "second_emoji_codepoint": second_codepoint,
            },
            timeout=30,
        )


def extract_two_codepoints_from_supported_payload(payload: dict) -> tuple[str, str]:
    categories = payload.get("categories", [])
    codepoints: list[str] = []
    for category in categories:
        for emoji in category.get("emojis", []):
            codepoint = emoji.get("codepoint")
            if codepoint:
                codepoints.append(codepoint)
            if len(codepoints) >= 2:
                return codepoints[0], codepoints[1]
    raise ValueError("Supported emoji payload did not provide at least two codepoints")

