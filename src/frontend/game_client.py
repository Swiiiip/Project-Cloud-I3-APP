import requests


class GameClient:
    def __init__(self,
                 base_url: str):
        self._base_url = base_url

    def create_daily_challenge(self, game_id: str) -> dict:
        url = f"{self._base_url}/api/daily-challenge"
        response = requests.post(url, json={"game_id": game_id}, timeout=5)
        return response.json()

    def make_guess(self, game_id: str, emoji: str) -> dict:
        url = f"{self._base_url}/api/guess"
        payload = {"game_id": game_id, "guess": emoji}
        response = requests.post(url, json=payload, timeout=5)
        return response.json()

    def get_status(self, game_id: str) -> dict:
        url = f"{self._base_url}/api/game/{game_id}"
        response = requests.get(url, timeout=5)
        return response.json()

    def get_supported_emojis(self) -> list[str]:
        url = f"{self._base_url}/api/supported-emojis"
        response = requests.get(url, timeout=5)
        return response.json()["emojis"]
