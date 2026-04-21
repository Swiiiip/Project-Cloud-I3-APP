from fastapi import FastAPI, Query

from src.common.contracts.game_contracts import GameGuessRequest
from src.core.service.daily_challenge import DailyChallengeService
from src.core.service.emoji_kitchen import EmojiKitchenService
from src.persistence.challenge_storage.challenge_storage_factory import ChallengeStorageFactory
from src.persistence.emoji_repository.file_emoji_repository import FileEmojiRepository
from src.utils.path_handler import PathHandler


class GameServiceApp:
    def __init__(self):
        repo = FileEmojiRepository(PathHandler.root_dir() / "emojis.json")
        emoji_service = EmojiKitchenService(repo)
        challenge_storage = ChallengeStorageFactory.create(PathHandler.root_dir())
        self._game_service = DailyChallengeService(emoji_service, challenge_storage)
        self._app = FastAPI(title="Blurmoji Game Service")
        self._register_routes()

    @property
    def app(self) -> FastAPI:
        return self._app

    def _register_routes(self) -> None:
        self._app.add_api_route("/internal/game/start", self.start_game, methods=["GET"])
        self._app.add_api_route("/internal/game/guess", self.submit_guess, methods=["POST"])
        self._app.add_api_route("/internal/game/status", self.get_status, methods=["GET"])
        self._app.add_api_route("/internal/game/health", self.health, methods=["GET"])

    def start_game(self, session_id: str = Query(...)) -> dict:
        state = self._game_service.get_user_state(session_id)
        return state.model_dump()

    def submit_guess(self, payload: GameGuessRequest) -> dict:
        state = self._game_service.process_guess(payload.session_id, payload.guess)
        return state.model_dump()

    def get_status(self, session_id: str = Query(...)) -> dict:
        state = self._game_service.get_user_state(session_id)
        return state.model_dump()

    @staticmethod
    def health() -> dict:
        return {"status": "ok"}


def create_app() -> FastAPI:
    return GameServiceApp().app

