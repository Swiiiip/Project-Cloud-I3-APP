from typing import Optional

from fastapi import Body, Cookie, FastAPI, Request, Response

from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple
from src.services.gateway.internal_client import InternalServiceClient
from src.services.gateway.session.signed_cookie_session_resolver import SignedCookieSessionResolver


class GatewayApp:
    def __init__(self, internal_client: InternalServiceClient, session_resolver: SignedCookieSessionResolver):
        self._internal_client = internal_client
        self._session_resolver = session_resolver
        self._app = FastAPI(title="Blurmoji Gateway API")
        self._register_routes()

    @property
    def app(self) -> FastAPI:
        return self._app

    def _register_routes(self) -> None:
        self._app.add_api_route("/api/v1/daily/start", self.start_game, methods=["GET"])
        self._app.add_api_route("/api/v1/daily/supported_emojis", self.get_supported_emojis, methods=["GET"])
        self._app.add_api_route("/api/v1/daily/get_status", self.get_game_status, methods=["GET"])
        self._app.add_api_route("/api/v1/daily/guess", self.submit_guess, methods=["POST"])
        self._app.add_api_route("/api/v1/daily/render", self.render_image, methods=["GET"])
        self._app.add_api_route("/health", self.health, methods=["GET"])

    async def start_game(
        self,
        request: Request,
        response: Response,
        session_id: Optional[str] = Cookie(None),
    ) -> dict:
        resolved_session_id = await self._session_resolver.resolve(request, response, session_id)
        return self._internal_client.start_game(resolved_session_id)

    def get_supported_emojis(self) -> dict:
        return self._internal_client.get_supported_emojis()

    async def submit_guess(
        self,
        request: Request,
        response: Response,
        couple_codepoint_guess: EmojiCodepointCouple = Body(...),
        session_id: Optional[str] = Cookie(None),
    ) -> dict:
        resolved_session_id = await self._session_resolver.resolve(request, response, session_id)
        return self._internal_client.submit_guess(resolved_session_id, couple_codepoint_guess)

    async def get_game_status(
        self,
        request: Request,
        response: Response,
        session_id: Optional[str] = Cookie(None),
    ) -> dict:
        resolved_session_id = await self._session_resolver.resolve(request, response, session_id)
        return self._internal_client.get_status(resolved_session_id)

    async def render_image(
        self,
        request: Request,
        response: Response,
        session_id: Optional[str] = Cookie(None),
    ) -> Response:
        resolved_session_id = await self._session_resolver.resolve(request, response, session_id)
        return Response(content=self._internal_client.get_rendered_image(resolved_session_id), media_type="image/png")

    @staticmethod
    def health() -> dict:
        return {"status": "ok"}


def create_app(internal_client: InternalServiceClient, session_resolver: SignedCookieSessionResolver) -> FastAPI:
    return GatewayApp(internal_client, session_resolver).app
