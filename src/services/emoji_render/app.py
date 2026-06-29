import io

from fastapi import FastAPI, Query, Response

from src.core.gameplay.image_blur_processor import ImageBlurProcessingService
from src.services.emoji_render.game_engine_service_client import GameEngineServiceClient


class EmojiRenderServiceApp:
    def __init__(self, game_engine_client: GameEngineServiceClient, blur_levels: int):
        self._game_engine_client = game_engine_client
        self._image_service = ImageBlurProcessingService(blur_levels=blur_levels)
        self._app = FastAPI(title="Blurmoji Emoji Render Service")
        self._register_routes()

    @property
    def app(self) -> FastAPI:
        return self._app

    def _register_routes(self) -> None:
        self._app.add_api_route("/internal/emoji_render/image", self._render_image, methods=["GET"])
        self._app.add_api_route("/internal/emoji_render/health", self._health, methods=["GET"])

    def _render_image(self, session_id: str = Query(...)) -> Response:
        state = self._game_engine_client.get_status(session_id)
        if state.is_completed:
            pil_image = self._image_service.get_original_image(state.answer.result_image_url)
        else:
            pil_image = self._image_service.get_processed_image(
                state.answer.result_image_url,
                state.max_attempts - state.attempts,
            )
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        return Response(content=buffer.getvalue(), media_type="image/png")

    @staticmethod
    def _health() -> dict:
        return {"status": "ok"}


def create_app(game_engine_client: GameEngineServiceClient, blur_levels: int) -> FastAPI:
    return EmojiRenderServiceApp(game_engine_client, blur_levels).app
