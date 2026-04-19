import io
import uuid
from typing import Optional

from fastapi import APIRouter, Response, Body, Cookie, Depends, Request

from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple
from src.core.gameplay.image_blur_processor import ImageBlurProcessingService
from src.core.service.daily_challenge import DailyChallengeService
from src.core.service.emoji_kitchen import EmojiKitchenService


async def get_or_create_session(
        request: Request,
        response: Response,
        session_id: Optional[str] = Cookie(None)) -> str:
    if session_id:
        return session_id

    # If we are here, the client sent no cookie.
    # Only generate a new one if we are hitting the start endpoint
    if "/start" in request.url.path:
        new_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=new_id, path="/")
        return new_id

    # Otherwise, the client is trying to play without a session
    from fastapi import HTTPException
    raise HTTPException(status_code=403, detail="No active session found. Visit /start first.")


class DailyChallengeRouter:
    def __init__(self, game_service: DailyChallengeService, image_service: ImageBlurProcessingService,
                 emoji_service: EmojiKitchenService):
        self.router = APIRouter(prefix="/api/v1/daily", tags=["gameplay"])
        self.game_service = game_service
        self.image_service = image_service
        self.emoji_service = emoji_service
        self._register_routes()

    async def start_game(self, session_id: str = Depends(get_or_create_session)):
        state = self.game_service.get_user_state(session_id)
        return state.model_dump()

    async def get_supported_emojis(self):
        emojis = self.game_service.get_supported_emojis()
        return {"emojis": [emoji.to_dict() for emoji in emojis]}

    async def submit_guess(self,
                           couple_codepoint_guess: EmojiCodepointCouple = Body(...),
                           session_id: str = Depends(get_or_create_session)):
        state = self.game_service.process_guess(session_id, couple_codepoint_guess)
        return state.model_dump()

    async def get_game_status(self, session_id: str = Depends(get_or_create_session)):
        state = self.game_service.get_user_state(session_id)
        return state.model_dump()

    async def render_image(self, session_id: str = Depends(get_or_create_session)):
        state = self.game_service.get_user_state(session_id)
        pil_image = self.image_service.get_processed_image(
            state.answer.result_image_url,
            state.attempts
        )
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        return Response(content=buffer.getvalue(), media_type="image/png")

    def _register_routes(self):
        self.router.add_api_route("/start", self.start_game, methods=["GET"])
        self.router.add_api_route("/supported_emojis", self.get_supported_emojis, methods=["GET"])
        self.router.add_api_route("/get_status", self.get_game_status, methods=["GET"])
        self.router.add_api_route("/guess", self.submit_guess, methods=["POST"])
        self.router.add_api_route("/render", self.render_image, methods=["GET"])
