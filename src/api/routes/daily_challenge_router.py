import io
from typing import Optional

from fastapi import APIRouter, Response, Body, Cookie, Request
from starlette.concurrency import run_in_threadpool

from src.api.session.abstract_session_resolver import AbstractSessionResolver
from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple
from src.core.gameplay.image_blur_processor import ImageBlurProcessingService
from src.core.gameplay.daily_challenge import DailyChallengeService
from src.core.emoji.emoji_kitchen import EmojiKitchenService


class DailyChallengeRouter:
    def __init__(self, game_service: DailyChallengeService, image_service: ImageBlurProcessingService,
                 emoji_service: EmojiKitchenService, session_resolver: AbstractSessionResolver):
        self.router = APIRouter(prefix="/api/v1/daily", tags=["gameplay"])
        self.game_service = game_service
        self.image_service = image_service
        self.emoji_service = emoji_service
        self._session_resolver = session_resolver
        self._register_routes()

    async def start_game(self, request: Request, response: Response,
                         session_id: Optional[str] = Cookie(None)):
        resolved_session_id = await self._session_resolver.resolve(request=request, response=response, session_id=session_id)
        state = await run_in_threadpool(self.game_service.get_user_state, resolved_session_id)
        return state.model_dump()

    async def get_supported_emojis(self):
        payload = await run_in_threadpool(self.emoji_service.fetch_grouped_supported_emoji_payload)
        return {"categories": list(payload)}

    async def submit_guess(self,
                           request: Request,
                           response: Response,
                           couple_codepoint_guess: EmojiCodepointCouple = Body(...),
                           session_id: Optional[str] = Cookie(None)):
        resolved_session_id = await self._session_resolver.resolve(request=request, response=response, session_id=session_id)
        state = await run_in_threadpool(self.game_service.process_guess, resolved_session_id, couple_codepoint_guess)
        return state.model_dump()

    async def get_game_status(self, request: Request, response: Response,
                              session_id: Optional[str] = Cookie(None)):
        resolved_session_id = await self._session_resolver.resolve(request=request, response=response, session_id=session_id)
        state = await run_in_threadpool(self.game_service.get_user_state, resolved_session_id)
        return state.model_dump()

    async def render_image(self, request: Request, response: Response,
                           session_id: Optional[str] = Cookie(None)):
        resolved_session_id = await self._session_resolver.resolve(request=request, response=response, session_id=session_id)
        state = await run_in_threadpool(self.game_service.get_user_state, resolved_session_id)
        if state.is_completed:
            pil_image = await run_in_threadpool(self.image_service.get_original_image, state.answer.result_image_url)
        else:
            pil_image = await run_in_threadpool(
                self.image_service.get_processed_image,
                state.answer.result_image_url,
                state.max_attempts - state.attempts
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
