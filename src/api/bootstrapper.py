from fastapi import FastAPI

from src.api.routes.daily_challenge_router import DailyChallengeRouter
from src.core.gameplay.image_blur_processor import ImageBlurProcessingService
from src.core.service.daily_challenge import DailyChallengeService
from src.core.service.emoji_kitchen import EmojiKitchenService
from src.persistence.file_emoji_repository import FileEmojiRepository
from src.utils.path_handler import PathHandler


class BlurmojiApiBootstrapper:
    def __init__(self):
        self.app = FastAPI(title="Blurmoji API")

        repo = FileEmojiRepository(PathHandler.root_dir() / "emojis.json")

        emoji_kitchen_service = EmojiKitchenService(repo)
        game_service = DailyChallengeService(emoji_kitchen_service)

        image_blur_processor = ImageBlurProcessingService()
        self.daily_router = DailyChallengeRouter(game_service, image_blur_processor, emoji_kitchen_service)

        self._setup_routes()

    def _setup_routes(self):
        self.app.include_router(self.daily_router.router)
