from fastapi import FastAPI, Query

from src.persistence.challenge_storage.abstract_challenge_storage import AbstractChallengeStorage
from src.persistence.emoji_repository.file_emoji_repository import FileEmojiRepository
from src.services.game_engine.game_contracts import GameGuessRequest
from src.core.gameplay.daily_challenge import DailyChallengeService
from src.core.emoji.emoji_kitchen import EmojiKitchenService
from src.utils.path_handler import PathHandler


class GameEngineServiceApp:
    def __init__(self, challenge_storage: AbstractChallengeStorage, max_attempts: int):
        repo = FileEmojiRepository(PathHandler.emojis_file())
        emoji_service = EmojiKitchenService(repo)
        self._challenge_service = DailyChallengeService(emoji_service, challenge_storage, max_attempts)
        self._app = FastAPI(title="Blurmoji Game Engine Service")
        self._register_routes()

    @property
    def app(self) -> FastAPI:
        return self._app

    def _register_routes(self) -> None:
        self._app.add_api_route("/internal/game_engine/start", self._start_game, methods=["GET"])
        self._app.add_api_route("/internal/game_engine/guess", self._submit_guess, methods=["POST"])
        self._app.add_api_route("/internal/game_engine/status", self._get_status, methods=["GET"])
        self._app.add_api_route("/internal/game_engine/health", self._health, methods=["GET"])

    def _start_game(self, session_id: str = Query(...)) -> dict:
        state = self._challenge_service.get_user_state(session_id)
        return state.model_dump()

    def _submit_guess(self, payload: GameGuessRequest) -> dict:
        state = self._challenge_service.process_guess(payload.session_id, payload.guess)
        return state.model_dump()

    def _get_status(self, session_id: str = Query(...)) -> dict:
        state = self._challenge_service.get_user_state(session_id)
        return state.model_dump()

    @staticmethod
    def _health() -> dict:
        return {"status": "ok"}


def create_app(challenge_storage: AbstractChallengeStorage, max_attempts: int) -> FastAPI:
    return GameEngineServiceApp(challenge_storage, max_attempts).app
