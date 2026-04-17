from fastapi import APIRouter, Response, Body

from src.core.gameplay.mode.challenge_state import ChallengeState
from src.core.service.emoji_kitchen import EmojiKitchenService
from src.core.gameplay.image_blur_processor import ImageBlurProcessingService
from src.core.service.daily_challenge import DailyChallengeService


class DailyChallengeRouter:
    def __init__(self, game_service: DailyChallengeService, image_service: ImageBlurProcessingService, emoji_service: EmojiKitchenService):
        self.router = APIRouter(prefix="/api/v1/daily", tags=["gameplay"])
        self.game_service = game_service
        self.image_service = image_service

        self._register_routes()

    async def start_game(self, user_id: str):
        state = self.game_service.get_user_state(user_id)
        return self._format_ui_response(state, user_id)

    async def get_supported_emojis(self):
        emojis = self.game_service.get_supported_emojis()
        return {"emojis": [emoji.to_dict() for emoji in emojis]}

    async def submit_guess(self, user_id: str, first_codepoint_guess: str = Body(...), second_codepoint_guess: str = Body(...)):
        state = self.game_service.process_guess(user_id, first_codepoint_guess, second_codepoint_guess)
        return self._format_ui_response(state, user_id)

    async def get_game_status(self, user_id: str):
        state = self.game_service.get_user_state(user_id)
        return self._format_ui_response(state, user_id)

    async def render_image(self, user_id: str):
        state = self.game_service.get_user_state(user_id)
        image_data = self.image_service.get_processed_image(state.answer.result_image_url, state.attempts)
        return Response(content=image_data.getvalue(), media_type="image/png")

    def _register_routes(self):
        self.router.add_api_route("/start/{user_id}", self.start_game, methods=["GET"])
        self.router.add_api_route("/supported_emojis", self.get_supported_emojis, methods=["GET"])
        self.router.add_api_route("/get_status/{user_id}", self.get_game_status, methods=["GET"])
        self.router.add_api_route("/guess/{user_id}", self.submit_guess, methods=["POST"])
        self.router.add_api_route("/render/{user_id}", self.render_image, methods=["GET"])

    @staticmethod
    def _format_ui_response(state: ChallengeState, user_id: str):
        return {
            "image_url": f"/api/v1/daily/render/{user_id}?t={state.attempts}",
            "attempts": state.attempts,
            "max_attempts": state.max_attempts,
            "is_completed": state.is_completed,
            "is_won": state.is_completed and state.attempts < state.max_attempts
        }
