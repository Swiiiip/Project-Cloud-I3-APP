from fastapi import FastAPI

from src.api.routes.daily_challenge_router import DailyChallengeRouter
from src.api.session.cookie_session_resolver import CookieSessionResolver
from src.core.gameplay.image_blur_processor import ImageBlurProcessingService
from src.core.service.daily_challenge import DailyChallengeService
from src.core.service.emoji_kitchen import EmojiKitchenService
from src.persistence.challenge_storage_factory import ChallengeStorageFactory
from src.persistence.file_emoji_repository import FileEmojiRepository
from src.utils.path_handler import PathHandler


class BlurmojiApiBootstrapper:
    def __init__(self):
        self._app = FastAPI(title="Blurmoji API")

        repo = FileEmojiRepository(PathHandler.root_dir() / "emojis.json")
        emoji_kitchen_service = EmojiKitchenService(repo)
        challenge_repository = ChallengeStorageFactory.create(PathHandler.root_dir())
        game_service = DailyChallengeService(emoji_kitchen_service, challenge_repository)
        image_blur_processor = ImageBlurProcessingService()
        session_resolver = CookieSessionResolver()

        self._daily_router = DailyChallengeRouter(game_service, image_blur_processor, emoji_kitchen_service, session_resolver)
        self._setup_routes()


    def _setup_routes(self):
        self._app.include_router(self._daily_router.router)
