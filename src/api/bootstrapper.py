from fastapi import FastAPI, Request, Response

from src.api.routes.daily_challenge_router import DailyChallengeRouter
from src.core.gameplay.image_blur_processor import ImageBlurProcessingService
from src.core.service.daily_challenge import DailyChallengeService
from src.core.service.emoji_kitchen import EmojiKitchenService
from src.persistence.file_challenge_storage import FileChallengeStorage
from src.persistence.file_emoji_repository import FileEmojiRepository
from src.utils.path_handler import PathHandler


class BlurmojiApiBootstrapper:
    def __init__(self):
        self._app = FastAPI(title="Blurmoji API")

        repo = FileEmojiRepository(PathHandler.root_dir() / "emojis.json")
        emoji_kitchen_service = EmojiKitchenService(repo)
        challenge_repository = FileChallengeStorage(PathHandler.src_dir / "daily.json")
        game_service = DailyChallengeService(emoji_kitchen_service, challenge_repository)
        image_blur_processor = ImageBlurProcessingService()

        self._daily_router = DailyChallengeRouter(game_service, image_blur_processor, emoji_kitchen_service)

        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        @self._app.middleware("http")
        async def session_cookie_middleware(request: Request, call_next):
            response = await call_next(request)
            if hasattr(request.state, "session_id"):
                response.set_cookie(
                    key="session_id",
                    value=request.state.session_id,
                    httponly=True,
                    samesite="lax",
                    secure=True,
                    path="/"
                )
            return response

    def _setup_routes(self):
        self._app.include_router(self._daily_router.router)
