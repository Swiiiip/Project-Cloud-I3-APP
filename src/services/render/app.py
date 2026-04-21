import io

from fastapi import FastAPI, Query, Response

from src.config import Config
from src.core.gameplay.image_blur_processor import ImageBlurProcessingService
from src.services.render.game_service_client import GameServiceClient


class RenderServiceApp:
    def __init__(self, game_client: GameServiceClient):
        self._game_client = game_client
        self._image_service = ImageBlurProcessingService(blur_levels=Config.DAILY_CHALLENGE_MAX_GUESSES)
        self._app = FastAPI(title="Blurmoji Render Service")
        self._register_routes()

    @property
    def app(self) -> FastAPI:
        return self._app

    def _register_routes(self) -> None:
        self._app.add_api_route("/internal/render/image", self.render_image, methods=["GET"])
        self._app.add_api_route("/internal/render/health", self.health, methods=["GET"])

    def render_image(self, session_id: str = Query(...)) -> Response:
        state = self._game_client.get_status(session_id)
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
    def health() -> dict:
        return {"status": "ok"}


def create_app(game_client: GameServiceClient) -> FastAPI:
    return RenderServiceApp(game_client).app

